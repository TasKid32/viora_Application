import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../utils/logger.dart';

/// JWT token manager with **in-memory cache**.
///
/// Reads from SecureStorage ONCE, then serves from RAM.
/// This eliminates 5-50ms platform channel overhead per request.
class TokenManager {
  static const _tag = 'TokenManager';
  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';

  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  // ─── In-memory cache ──────────────────────────────────
  String? _cachedAccessToken;
  String? _cachedRefreshToken;

  /// Load tokens from SecureStorage into RAM. Call once at app start.
  Future<void> init() async {
    try {
      _cachedAccessToken = await _storage.read(key: _accessKey);
      _cachedRefreshToken = await _storage.read(key: _refreshKey);
      Log.d(_tag, 'Tokens loaded: access=${_cachedAccessToken != null}, refresh=${_cachedRefreshToken != null}');
    } catch (e) {
      Log.e(_tag, 'Failed to load tokens', e);
    }
  }

  /// Get access token — returns from RAM (instant, no I/O).
  String? get accessToken => _cachedAccessToken;

  /// Get refresh token — returns from RAM.
  String? get refreshToken => _cachedRefreshToken;

  /// Check if user is authenticated.
  bool get isAuthenticated => _cachedAccessToken != null && !isExpired;

  /// Save tokens (persists to SecureStorage + updates RAM cache).
  Future<void> saveTokens({required String access, required String refresh}) async {
    _cachedAccessToken = access;
    _cachedRefreshToken = refresh;
    await _storage.write(key: _accessKey, value: access);
    await _storage.write(key: _refreshKey, value: refresh);
    Log.d(_tag, 'Tokens saved');
  }

  /// Clear all tokens (logout).
  Future<void> clear() async {
    _cachedAccessToken = null;
    _cachedRefreshToken = null;
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
    Log.d(_tag, 'Tokens cleared');
  }

  /// Check if access token is expired by decoding JWT payload.
  bool get isExpired {
    final token = _cachedAccessToken;
    if (token == null) return true;

    try {
      final parts = token.split('.');
      if (parts.length != 3) return true;

      final payload = utf8.decode(base64Url.decode(base64Url.normalize(parts[1])));
      final Map<String, dynamic> data = json.decode(payload);
      final exp = data['exp'] as int?;
      if (exp == null) return true;

      return DateTime.now().isAfter(
        DateTime.fromMillisecondsSinceEpoch(exp * 1000),
      );
    } catch (_) {
      return true;
    }
  }
}
