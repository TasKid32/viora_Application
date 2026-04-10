import 'package:flutter/foundation.dart';

/// Lightweight logger — only prints in debug mode.
class Log {
  Log._();

  static void d(String tag, String message) {
    if (kDebugMode) debugPrint('[$tag] $message');
  }

  static void e(String tag, String message, [Object? error]) {
    if (kDebugMode) debugPrint('❌ [$tag] $message${error != null ? ': $error' : ''}');
  }

  static void w(String tag, String message) {
    if (kDebugMode) debugPrint('⚠️ [$tag] $message');
  }
}
