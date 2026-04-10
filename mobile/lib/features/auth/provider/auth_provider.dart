import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import '../../../core/auth/token_manager.dart';
import '../../../core/routing/app_router.dart';
import '../../../core/utils/logger.dart';
import '../../../core/utils/error_helper.dart';
import '../data/auth_api.dart';
import '../data/auth_models.dart';

/// Auth provider — manages login/register state.
///
/// Also syncs auth state with [AuthStateNotifier] so GoRouter
/// re-evaluates redirects without recreating the router.
class AuthProvider extends ChangeNotifier {
  static const _tag = 'Auth';

  final AuthApi _api;
  final TokenManager _tokenManager;
  final AuthStateNotifier _authNotifier;

  /// Expose API for screens that need direct API calls (e.g. forgot password).
  AuthApi get api => _api;

  AuthProvider({
    required AuthApi api,
    required TokenManager tokenManager,
    required AuthStateNotifier authNotifier,
  })  : _api = api,
        _tokenManager = tokenManager,
        _authNotifier = authNotifier;

  // ─── State ──────────────────────────────────────────
  User? _user;
  bool _loading = false;
  String? _error;

  User? get user => _user;
  bool get loading => _loading;
  String? get error => _error;
  bool get isAuthenticated => _tokenManager.isAuthenticated;

  void clearError() {
    _error = null;
    notifyListeners();
  }

  /// Sync GoRouter auth state.
  void _syncAuthState() {
    _authNotifier.isAuthenticated = _tokenManager.isAuthenticated;
  }

  // ─── Login ──────────────────────────────────────────
  Future<bool> login({required String email, required String password}) async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.login(email: email, password: password);
      await _tokenManager.saveTokens(
        access: response.accessToken,
        refresh: response.refreshToken,
      );
      _user = response.user;
      _syncAuthState();
      Log.d(_tag, 'Login success: ${response.user.name}');
      return true;
    } on DioException catch (e) {
      _error = extractDioError(e);
      Log.e(_tag, 'Login failed', _error);
      return false;
    } catch (e) {
      _error = 'An unexpected error occurred';
      Log.e(_tag, 'Login unexpected error', e);
      return false;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  // ─── Register ───────────────────────────────────────
  Future<bool> register({
    required String name,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.register(
        name: name,
        email: email,
        password: password,
        confirmPassword: confirmPassword,
      );
      await _tokenManager.saveTokens(
        access: response.accessToken,
        refresh: response.refreshToken,
      );
      _user = response.user;
      _syncAuthState();
      Log.d(_tag, 'Register success: ${response.user.name}');
      return true;
    } on DioException catch (e) {
      _error = extractDioError(e);
      Log.e(_tag, 'Register failed', _error);
      return false;
    } catch (e) {
      _error = 'An unexpected error occurred';
      Log.e(_tag, 'Register unexpected error', e);
      return false;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  // ─── Logout ─────────────────────────────────────────
  Future<void> logout() async {
    await _tokenManager.clear();
    _user = null;
    _syncAuthState();
    notifyListeners();
  }
}
