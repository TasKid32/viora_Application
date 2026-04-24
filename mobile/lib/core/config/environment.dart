import 'package:flutter/foundation.dart';

/// Environment configuration — resolved at build time.
class Environment {
  Environment._();

  static const String _buildTimeApiUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://10.0.2.2:8000',
    
  );

  static const bool isDevelopment = !kReleaseMode;

  static String get apiBaseUrl => isDevelopment ? _buildTimeApiUrl : 'https://api.viora.com';

  /// Timeouts in seconds.
  static const int connectTimeout = 15;
  static const int receiveTimeout = 30;
  static const int uploadTimeout = 60;

  /// File constraints.
  static const int maxFileSizeMB = 10;
}
