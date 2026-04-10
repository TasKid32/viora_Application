import 'dart:async';
import 'dart:ui';
import 'package:dio/dio.dart';
import '../config/environment.dart';
import '../auth/token_manager.dart';
import '../api/api_endpoints.dart';
import '../api/retry_interceptor.dart';
import '../api/quota_interceptor.dart';
import '../utils/logger.dart';

/// Singleton HTTP client with automatic token refresh on 401.
///
/// Key features:
/// - Attaches access token from RAM cache (instant, no I/O)
/// - Intercepts 401 → refreshes token → retries original request
/// - Uses Completer to prevent race conditions on concurrent 401s
/// - Uses SEPARATE Dio instance for refresh to avoid infinite loop
/// - RetryInterceptor — exponential backoff on connection/server errors
/// - QuotaInterceptor — handles 403/429 rate limit errors
class ApiClient {
  static const _tag = 'API';

  late final Dio _dio;
  final TokenManager _tokenManager;

  /// Callback to force logout when refresh token is also expired.
  VoidCallback? onForceLogout;

  // ─── Token refresh state ──────────────────────────────
  bool _isRefreshing = false;
  Completer<bool>? _refreshCompleter;

  /// Separate Dio instance for token refresh — NO auth interceptor!
  late final Dio _refreshDio;

  ApiClient(this._tokenManager) {
    // Main Dio with auth interceptor
    _dio = Dio(BaseOptions(
      baseUrl: Environment.apiBaseUrl,
      connectTimeout: Duration(seconds: Environment.connectTimeout),
      receiveTimeout: Duration(seconds: Environment.receiveTimeout),
      sendTimeout: Duration(seconds: Environment.uploadTimeout),
      headers: {'Accept': 'application/json'},
    ));

    _dio.interceptors.addAll([
      InterceptorsWrapper(
        onRequest: _onRequest,
        onResponse: _onResponse,
        onError: _onError,
      ),
      RetryInterceptor(_dio),
      QuotaInterceptor(),
    ]);

    // Separate Dio for refresh — no interceptors to avoid infinite loop!
    _refreshDio = Dio(BaseOptions(
      baseUrl: Environment.apiBaseUrl,
      connectTimeout: Duration(seconds: Environment.connectTimeout),
      receiveTimeout: Duration(seconds: Environment.receiveTimeout),
      headers: {'Accept': 'application/json'},
    ));
  }

  // ─── Interceptors ──────────────────────────────────────

  void _onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Token from RAM — instant, no async I/O!
    final token = _tokenManager.accessToken;
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    Log.d(_tag, '→ ${options.method} ${options.path}');
    handler.next(options);
  }

  void _onResponse(Response response, ResponseInterceptorHandler handler) {
    Log.d(_tag, '← ${response.statusCode} ${response.requestOptions.path}');
    handler.next(response);
  }

  Future<void> _onError(DioException err, ErrorInterceptorHandler handler) async {
    // Only handle 401 Unauthorized
    if (err.response?.statusCode != 401) {
      Log.e(_tag, '✗ ${err.requestOptions.path}', err.message);
      return handler.next(err);
    }

    // Don't try to refresh if this IS the refresh request
    if (err.requestOptions.path == Endpoints.refresh) {
      Log.e(_tag, '✗ Refresh token also expired — forcing logout');
      await _tokenManager.clear();
      onForceLogout?.call();
      return handler.next(err);
    }

    Log.w(_tag, '⟳ 401 on ${err.requestOptions.path} — attempting token refresh');

    // Try to refresh the token
    final refreshed = await _tryRefreshToken();

    if (refreshed) {
      // Retry original request with new token
      final retryOptions = err.requestOptions;
      retryOptions.headers['Authorization'] = 'Bearer ${_tokenManager.accessToken}';
      try {
        final response = await _dio.fetch(retryOptions);
        return handler.resolve(response);
      } catch (retryError) {
        Log.e(_tag, '✗ Retry failed after refresh', retryError);
        return handler.next(err);
      }
    } else {
      // Refresh failed — propagate original error
      return handler.next(err);
    }
  }

  // ─── Token refresh logic ───────────────────────────────

  /// Attempts to refresh the access token.
  /// Uses Completer pattern to prevent concurrent refresh requests.
  Future<bool> _tryRefreshToken() async {
    // If already refreshing, wait for the ongoing refresh
    if (_isRefreshing) {
      Log.d(_tag, '⟳ Waiting for ongoing refresh...');
      return _refreshCompleter!.future;
    }

    _isRefreshing = true;
    _refreshCompleter = Completer<bool>();

    try {
      final refreshToken = _tokenManager.refreshToken;
      if (refreshToken == null) {
        Log.e(_tag, '✗ No refresh token available');
        _completeRefresh(false);
        return false;
      }

      // Call refresh endpoint using SEPARATE Dio (no auth interceptor!)
      final response = await _refreshDio.post(
        Endpoints.refresh,
        data: {'refresh_token': refreshToken},
      );

      final newAccess = response.data['access_token'] as String?;
      final newRefresh = response.data['refresh_token'] as String?;

      if (newAccess != null && newRefresh != null) {
        await _tokenManager.saveTokens(access: newAccess, refresh: newRefresh);
        Log.d(_tag, '✓ Token refreshed successfully');
        _completeRefresh(true);
        return true;
      } else {
        Log.e(_tag, '✗ Refresh response missing tokens');
        _completeRefresh(false);
        return false;
      }
    } catch (e) {
      Log.e(_tag, '✗ Token refresh failed', e);
      await _tokenManager.clear();
      onForceLogout?.call();
      _completeRefresh(false);
      return false;
    }
  }

  void _completeRefresh(bool success) {
    _refreshCompleter?.complete(success);
    _isRefreshing = false;
    _refreshCompleter = null;
  }

  // ─── Public API ──────────────────────────────────────

  Future<Response> get(String path, {Map<String, dynamic>? params}) {
    return _dio.get(path, queryParameters: params);
  }

  Future<Response> post(String path, {dynamic data, Options? options}) {
    return _dio.post(path, data: data, options: options);
  }

  Future<Response> put(String path, {dynamic data}) {
    return _dio.put(path, data: data);
  }

  Future<Response> delete(String path) {
    return _dio.delete(path);
  }

  /// Upload file with progress tracking.
  Future<Response> upload(
    String path, {
    required FormData data,
    void Function(int sent, int total)? onProgress,
  }) {
    return _dio.post(
      path,
      data: data,
      options: Options(receiveTimeout: Duration(seconds: Environment.uploadTimeout)),
      onSendProgress: onProgress,
    );
  }
}
