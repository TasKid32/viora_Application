import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import '../../../core/utils/logger.dart';
import '../../../core/utils/error_helper.dart';
import '../data/analysis_api.dart';
import '../data/analysis_models.dart';

/// Analysis stages for UI progress display (4-step pipeline).
enum AnalysisStage {
  idle,
  uploading,    // Step 1: Uploading file to server
  extracting,   // Step 2: Extracting text from PDF/DOCX
  analyzing,    // Step 3: Running NER AI model on text
  matching,     // Step 4: Matching skills with O*NET database
  complete,
  error,
}

/// Analysis provider — manages upload + analyze flow.
///
/// Key improvements over old version:
/// - Only 2 notifyListeners calls (start + end)
/// - Real upload progress percentage
/// - Clean stage tracking
class AnalysisProvider extends ChangeNotifier {
  static const _tag = 'Analysis';

  final AnalysisApi _api;
  AnalysisProvider({required AnalysisApi api}) : _api = api;

  // ─── State ──────────────────────────────────────────
  AnalysisStage _stage = AnalysisStage.idle;
  double _uploadProgress = 0.0;
  AnalysisResult? _result;
  String? _error;

  AnalysisStage get stage => _stage;
  double get uploadProgress => _uploadProgress;
  AnalysisResult? get result => _result;
  String? get error => _error;
  bool get isLoading =>
      _stage == AnalysisStage.uploading ||
      _stage == AnalysisStage.extracting ||
      _stage == AnalysisStage.analyzing ||
      _stage == AnalysisStage.matching;

  /// Reset state for new analysis.
  void reset() {
    _stage = AnalysisStage.idle;
    _uploadProgress = 0.0;
    _result = null;
    _error = null;
    notifyListeners();
  }

  /// Upload and analyze resume file.
  Future<void> analyzeFile({
    required String filePath,
    required String fileName,
    List<String>? additionalSkills,
  }) async {
    _stage = AnalysisStage.uploading;
    _uploadProgress = 0.0;
    _error = null;
    notifyListeners();

    try {
      // Step 1: Upload with real progress
      Log.d(_tag, 'Uploading: $fileName');
      final fileId = await _api.uploadResume(
        filePath: filePath,
        fileName: fileName,
        onProgress: (progress) {
          _uploadProgress = progress;
          notifyListeners();
        },
      );

      // Steps 2-4: Use SSE streaming for real-time stage updates
      _stage = AnalysisStage.extracting;
      notifyListeners();

      Log.d(_tag, 'Starting SSE analysis: $fileId');

      try {
        _result = await _api.analyzeResumeStream(
          fileId: fileId,
          additionalSkills: additionalSkills,
          onStage: (step) {
            // Map backend step names to AnalysisStage enum
            switch (step) {
              case 'extracting_text':
                _stage = AnalysisStage.extracting;
                break;
              case 'running_ner':
                _stage = AnalysisStage.analyzing;
                break;
              case 'matching_onet':
                _stage = AnalysisStage.matching;
                break;
            }
            notifyListeners();
          },
        );
      } catch (_) {
        // SSE failed — fallback to regular analyze
        Log.d(_tag, 'SSE failed, falling back to regular analyze');
        _stage = AnalysisStage.analyzing;
        notifyListeners();

        _result = await _api.analyzeResume(
          fileId: fileId,
          additionalSkills: additionalSkills,
        );
      }

      _stage = AnalysisStage.complete;
      Log.d(_tag, 'Complete: ${_result!.predictedJob}');
    } on DioException catch (e) {
      _stage = AnalysisStage.error;
      _error = extractDioError(e);
      Log.e(_tag, 'Failed', _error);
    } catch (e) {
      _stage = AnalysisStage.error;
      _error = 'An unexpected error occurred';
      Log.e(_tag, 'Unexpected error', e);
    }
    notifyListeners();
  }

}
