import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import '../../../core/utils/logger.dart';
import '../../../core/utils/error_helper.dart';
import '../data/roadmap_api.dart';

/// Roadmap provider — manages roadmap state with per-topic resource tracking.
class RoadmapProvider extends ChangeNotifier {
  static const _tag = 'Roadmap';

  final RoadmapApi _api;
  RoadmapProvider({required RoadmapApi api}) : _api = api;

  RoadmapData? _data;
  bool _loading = false;
  bool _generating = false;
  String? _error;

  RoadmapData? get data => _data;
  bool get loading => _loading;
  bool get generating => _generating;
  String? get error => _error;
  bool get hasRoadmap => _data != null && _data!.phases.isNotEmpty;

  /// Total resources across all phases (flattened from all topics).
  int get totalResources {
    if (_data == null) return 0;
    return _data!.phases.fold(0, (sum, p) => sum + p.allResources.length);
  }

  /// Completed resources across all phases.
  int get completedResources {
    if (_data == null) return 0;
    return _data!.phases.fold(
      0, (sum, p) => sum + p.allResources.where((r) => r.completed).length,
    );
  }

  /// Overall progress percentage (0-100).
  int get progressPercent {
    final total = totalResources;
    if (total == 0) return 0;
    return ((completedResources / total) * 100).round();
  }

  /// Total topics across all phases.
  int get totalTopics {
    if (_data == null) return 0;
    return _data!.phases.fold(0, (sum, p) => sum + p.topics.length);
  }

  /// Completed topics (all resources in topic are done).
  int get completedTopics {
    if (_data == null) return 0;
    return _data!.phases.fold(
      0,
      (sum, p) => sum + p.topics.where((t) => t.completed).length,
    );
  }

  /// Completed resources count for a specific phase.
  int completedInPhase(int phaseIndex) {
    if (_data == null || phaseIndex >= _data!.phases.length) return 0;
    return _data!.phases[phaseIndex].allResources.where((r) => r.completed).length;
  }

  /// Total resources in phase.
  int totalInPhase(int phaseIndex) {
    if (_data == null || phaseIndex >= _data!.phases.length) return 0;
    return _data!.phases[phaseIndex].allResources.length;
  }

  /// Load existing roadmap.
  Future<void> load({String? analysisId}) async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      _data = await _api.getRoadmap(analysisId: analysisId);
      Log.d(_tag, 'Loaded: ${_data!.phases.length} phases, $totalResources resources, $totalTopics topics');
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        _data = null; // No roadmap yet — not an error
      } else {
        _error = extractDioError(e);
        Log.e(_tag, 'Load failed', _error);
      }
    } catch (e) {
      _error = 'An unexpected error occurred';
      Log.e(_tag, 'Unexpected', e);
    }

    _loading = false;
    notifyListeners();
  }

  /// Generate new roadmap from analysis.
  Future<void> generate(String analysisId) async {
    _generating = true;
    _error = null;
    notifyListeners();

    try {
      _data = await _api.generateRoadmap(analysisId);
      Log.d(_tag, 'Generated: ${_data!.phases.length} phases, $totalTopics topics');
    } on DioException catch (e) {
      _error = extractDioError(e);
      Log.e(_tag, 'Generate failed', _error);
    } catch (e) {
      _error = 'An unexpected error occurred';
      Log.e(_tag, 'Unexpected', e);
    }

    _generating = false;
    notifyListeners();
  }

  /// Toggle individual resource completion (per-topic tracking).
  Future<void> toggleResource(int phaseIndex, int topicIndex, int resourceIndex) async {
    if (_data == null) return;
    if (phaseIndex >= _data!.phases.length) return;
    final phase = _data!.phases[phaseIndex];
    if (topicIndex >= phase.topics.length) return;
    final topic = phase.topics[topicIndex];
    if (resourceIndex >= topic.resources.length) return;

    final resource = topic.resources[resourceIndex];

    // Optimistic update
    resource.completed = !resource.completed;
    // Auto-compute phase completion
    phase.completed = phase.allResources.every((r) => r.completed);
    notifyListeners();

    try {
      final resourceId = '${topicIndex}_$resourceIndex';
      await _api.toggleResource(phaseIndex, 0, resourceId: resourceId);
    } catch (e) {
      // Rollback on error
      resource.completed = !resource.completed;
      phase.completed = phase.allResources.every((r) => r.completed);
      notifyListeners();
      Log.e(_tag, 'Toggle resource failed', e);
    }
  }

  /// Toggle step completion (legacy — keeps backward compatibility).
  Future<void> toggleStep(int index) async {
    if (_data == null || index >= _data!.phases.length) return;

    final phase = _data!.phases[index];
    final newState = !phase.completed;

    // Optimistic update
    phase.completed = newState;
    // When toggling phase, toggle all resources in all topics
    for (final topic in phase.topics) {
      for (final r in topic.resources) {
        r.completed = newState;
      }
    }
    notifyListeners();

    try {
      if (newState) {
        await _api.markStepComplete(index);
      } else {
        await _api.markStepIncomplete(index);
      }
    } catch (e) {
      // Rollback on error
      phase.completed = !newState;
      for (final topic in phase.topics) {
        for (final r in topic.resources) {
          r.completed = !newState;
        }
      }
      notifyListeners();
      Log.e(_tag, 'Toggle failed', e);
    }
  }

}
