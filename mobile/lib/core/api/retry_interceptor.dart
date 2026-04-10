import 'package:dio/dio.dart';
import '../utils/logger.dart';

/// Retry interceptor — exponential backoff with 3 retries.
///
/// Retries on connection errors and 5xx server errors.
/// Backoff: 1s → 2s → 4s.
class RetryInterceptor extends Interceptor {
  static const _tag = 'Retry';
  static const _maxRetries = 3;

  final Dio _dio;
  RetryInterceptor(this._dio);

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    if (_shouldRetry(err)) {
      final extra = err.requestOptions.extra;
      final retryCount = (extra['_retryCount'] as int?) ?? 0;

      if (retryCount < _maxRetries) {
        final delay = Duration(seconds: 1 << retryCount); // 1s, 2s, 4s
        Log.d(_tag, 'Retry ${retryCount + 1}/$_maxRetries after ${delay.inSeconds}s');

        await Future.delayed(delay);

        // Clone request with incremented retry count
        final options = err.requestOptions;
        options.extra['_retryCount'] = retryCount + 1;

        try {
          final response = await _dio.fetch(options);
          return handler.resolve(response);
        } on DioException catch (e) {
          return super.onError(e, handler);
        }
      }
    }
    super.onError(err, handler);
  }

  bool _shouldRetry(DioException err) {
    // Retry on connection errors
    if (err.type == DioExceptionType.connectionError ||
        err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.sendTimeout ||
        err.type == DioExceptionType.receiveTimeout) {
      return true;
    }
    // Retry on 5xx server errors
    final statusCode = err.response?.statusCode ?? 0;
    if (statusCode >= 500 && statusCode < 600) {
      return true;
    }
    return false;
  }
}
