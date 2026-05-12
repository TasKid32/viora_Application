import 'package:flutter/foundation.dart';

/// Environment configuration — resolved at build time.
class Environment {
  Environment._();

  static const String _buildTimeApiUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://192.168.0.114:8000',
  ); 

  static const bool isDevelopment = !kReleaseMode;

  static String get apiBaseUrl =>
      isDevelopment ? _buildTimeApiUrl : 'https://api.viora.com';

//API Configuration for Avatar
  static const String apiBaseU =
      'http://192.168.0.114:8000'; //Replace with your actual API base URL for avatar

  /// Timeouts in seconds.
  static const int connectTimeout = 15;
  static const int receiveTimeout = 30;
  static const int uploadTimeout = 60;

  /// File constraints.
  static const int maxFileSizeMB = 10;
}
