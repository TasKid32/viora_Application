import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import 'auth_models.dart';

/// Auth API service — thin wrapper around ApiClient.
class AuthApi {
  final ApiClient _api;
  AuthApi(this._api);

  Future<AuthResponse> register({
    required String name,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    final response = await _api.post(Endpoints.register, data: {
      'full_name': name,
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
    });
    return AuthResponse.fromJson(response.data);
  }

  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final response = await _api.post(Endpoints.login, data: {
      'email': email,
      'password': password,
    });
    return AuthResponse.fromJson(response.data);
  }

  Future<Map<String, dynamic>> refreshToken(String refreshToken) async {
    final response = await _api.post(Endpoints.refresh, data: {
      'refresh_token': refreshToken,
    });
    return response.data;
  }

  /// Request password reset link via email.
  Future<void> forgotPassword(String email) async {
    await _api.post(Endpoints.forgotPassword, data: {'email': email});
  }
}
