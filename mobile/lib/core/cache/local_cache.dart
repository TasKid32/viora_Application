import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/logger.dart';

/// Simple local cache using SharedPreferences — Cache-First strategy.
///
/// Caches JSON responses with expiration. On network failure, returns cached data.
/// This provides basic offline support without heavy dependencies like Hive.
class LocalCache {
  static const _tag = 'Cache';
  static const _prefix = 'cache_';
  static const _metaPrefix = 'cache_meta_';

  static SharedPreferences? _prefs;

  static Future<SharedPreferences> _getPrefs() async {
    return _prefs ??= await SharedPreferences.getInstance();
  }

  /// Default cache duration: 30 minutes.
  static const Duration defaultTtl = Duration(minutes: 30);

  /// Save data to cache with timestamp.
  static Future<void> put(String key, dynamic data, {Duration? ttl}) async {
    try {
      final prefs = await _getPrefs();
      final jsonStr = jsonEncode(data);
      await prefs.setString('$_prefix$key', jsonStr);
      await prefs.setInt('$_metaPrefix$key', DateTime.now().millisecondsSinceEpoch);
      Log.d(_tag, 'Cached: $key (${jsonStr.length} chars)');
    } catch (e) {
      Log.e(_tag, 'Failed to cache $key', e);
    }
  }

  /// Get cached data if it exists and isn't expired.
  static Future<dynamic> get(String key, {Duration? ttl}) async {
    try {
      final prefs = await _getPrefs();
      final jsonStr = prefs.getString('$_prefix$key');
      final timestamp = prefs.getInt('$_metaPrefix$key');

      if (jsonStr == null || timestamp == null) return null;

      // Check expiration
      final age = DateTime.now().millisecondsSinceEpoch - timestamp;
      final maxAge = (ttl ?? defaultTtl).inMilliseconds;

      if (age > maxAge) {
        Log.d(_tag, 'Cache expired: $key');
        return null;
      }

      Log.d(_tag, 'Cache hit: $key');
      return jsonDecode(jsonStr);
    } catch (e) {
      Log.e(_tag, 'Failed to read cache $key', e);
      return null;
    }
  }

  /// Get cached data regardless of expiration (for offline fallback).
  static Future<dynamic> getStale(String key) async {
    try {
      final prefs = await _getPrefs();
      final jsonStr = prefs.getString('$_prefix$key');
      if (jsonStr == null) return null;
      Log.d(_tag, 'Stale cache hit: $key');
      return jsonDecode(jsonStr);
    } catch (e) {
      return null;
    }
  }

  /// Remove a specific cache entry.
  static Future<void> remove(String key) async {
    final prefs = await _getPrefs();
    await prefs.remove('$_prefix$key');
    await prefs.remove('$_metaPrefix$key');
  }

  /// Clear all cached data.
  static Future<void> clearAll() async {
    final prefs = await _getPrefs();
    final keys = prefs.getKeys().where((k) => k.startsWith(_prefix) || k.startsWith(_metaPrefix));
    for (final key in keys) {
      await prefs.remove(key);
    }
    Log.d(_tag, 'Cache cleared');
  }
}
