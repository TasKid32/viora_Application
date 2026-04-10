import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../../../core/utils/logger.dart';
import '../../../core/utils/error_helper.dart';

/// Profile provider — manages profile data + avatar upload.
class ProfileProvider extends ChangeNotifier {
  final ApiClient _api;
  ProfileProvider({required ApiClient api}) : _api = api;

  Map<String, dynamic>? _profile;
  bool _loading = false;
  bool _uploadingAvatar = false;
  String? _error;

  Map<String, dynamic>? get profile => _profile;
  bool get loading => _loading;
  bool get uploadingAvatar => _uploadingAvatar;
  String? get error => _error;

  String? get avatarUrl => _profile?['avatar_url'] as String?;

  Future<void> load() async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      final res = await _api.get(Endpoints.profile);
      _profile = res.data;
    } on DioException catch (e) {
      _error = extractDioError(e);
      Log.e('Profile', 'Load failed', _error);
    } catch (e) {
      _error = 'An unexpected error occurred';
      Log.e('Profile', 'Load failed', e);
    }
    _loading = false;
    notifyListeners();
  }

  Future<bool> update(Map<String, dynamic> data) async {
    try {
      await _api.put(Endpoints.profile, data: data);
      await load();
      return true;
    } on DioException catch (e) {
      _error = extractDioError(e);
      notifyListeners();
      Log.e('Profile', 'Update failed', _error);
      return false;
    } catch (e) {
      _error = 'An unexpected error occurred';
      notifyListeners();
      Log.e('Profile', 'Update failed', e);
      return false;
    }
  }

  /// Upload avatar image file.
  Future<bool> uploadAvatar(String filePath) async {
    _uploadingAvatar = true;
    notifyListeners();
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath),
      });
      await _api.upload(Endpoints.profileAvatar, data: formData);
      await load(); // Reload profile to get new avatar_url
      return true;
    } catch (e) {
      Log.e('Profile', 'Avatar upload failed', e);
      return false;
    } finally {
      _uploadingAvatar = false;
      notifyListeners();
    }
  }
}
