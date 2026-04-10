import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import '../../../core/utils/logger.dart';
import '../../../core/utils/error_helper.dart';
import '../data/dashboard_api.dart';

/// Dashboard provider — loads dashboard data.
class DashboardProvider extends ChangeNotifier {
  static const _tag = 'Dashboard';

  final DashboardApi _api;
  DashboardProvider({required DashboardApi api}) : _api = api;

  DashboardData? _data;
  bool _loading = false;
  String? _error;

  DashboardData? get data => _data;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> load() async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      _data = await _api.getDashboard();
      Log.d(_tag, 'Loaded: ${_data!.userName}, progress=${_data!.overallProgress}%');
    } on DioException catch (e) {
      _error = extractDioError(e);
      Log.e(_tag, 'Load failed', _error);
    } catch (e) {
      _error = 'An unexpected error occurred';
      Log.e(_tag, 'Unexpected error', e);
    }

    _loading = false;
    notifyListeners();
  }
}
