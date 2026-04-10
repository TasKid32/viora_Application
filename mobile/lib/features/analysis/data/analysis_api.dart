import 'dart:convert';
import 'package:dio/dio.dart';
import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import 'analysis_models.dart';

/// Analysis API — uploads file & analyzes in optimized flow.
class AnalysisApi {
  final ApiClient _api;
  AnalysisApi(this._api);

  /// Upload resume file with real progress tracking.
  Future<String> uploadResume({
    required String filePath,
    required String fileName,
    void Function(double progress)? onProgress,
  }) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath, filename: fileName),
    });

    final response = await _api.upload(
      Endpoints.resumeUpload,
      data: formData,
      onProgress: (sent, total) {
        if (total > 0 && onProgress != null) {
          onProgress(sent / total);
        }
      },
    );

    return response.data['file_id'] as String;
  }

  /// Analyze uploaded resume.
  Future<AnalysisResult> analyzeResume({
    required String fileId,
    List<String>? additionalSkills,
  }) async {
    final response = await _api.post(
      Endpoints.resumeAnalyze,
      data: {
        'file_id': fileId,
        if (additionalSkills != null && additionalSkills.isNotEmpty)
          'additional_skills': additionalSkills,
      },
      options: Options(receiveTimeout: const Duration(seconds: 180)), // NER model needs time
    );

    return AnalysisResult.fromJson(response.data);
  }

  /// Analyze with SSE streaming — receives real-time stage updates.
  ///
  /// [onStage] is called with step names: 'extracting_text', 'running_ner', 'matching_onet'
  /// Returns the final AnalysisResult when the 'result' event arrives.
  Future<AnalysisResult> analyzeResumeStream({
    required String fileId,
    List<String>? additionalSkills,
    void Function(String step)? onStage,
  }) async {
    final response = await _api.post(
      Endpoints.resumeAnalyzeStream,
      data: {
        'file_id': fileId,
        if (additionalSkills != null && additionalSkills.isNotEmpty)
          'additional_skills': additionalSkills,
      },
      options: Options(
        responseType: ResponseType.stream,
        receiveTimeout: const Duration(seconds: 180),
      ),
    );

    // Parse SSE stream
    final stream = response.data.stream as Stream<List<int>>;
    final buffer = StringBuffer();
    String? currentEvent;
    Map<String, dynamic>? finalResult;

    await for (final chunk in stream) {
      buffer.write(String.fromCharCodes(chunk));
      
      // Process complete lines
      while (buffer.toString().contains('\n\n')) {
        final text = buffer.toString();
        final blockEnd = text.indexOf('\n\n');
        final block = text.substring(0, blockEnd);
        buffer.clear();
        buffer.write(text.substring(blockEnd + 2));

        // Parse SSE block
        for (final line in block.split('\n')) {
          if (line.startsWith('event: ')) {
            currentEvent = line.substring(7).trim();
          } else if (line.startsWith('data: ')) {
            final data = line.substring(6).trim();
            if (currentEvent == 'stage') {
              final parsed = _parseJson(data);
              if (parsed != null && onStage != null) {
                onStage(parsed['step'] as String? ?? '');
              }
            } else if (currentEvent == 'result') {
              finalResult = _parseJson(data);
            } else if (currentEvent == 'error') {
              final parsed = _parseJson(data);
              throw DioException(
                requestOptions: RequestOptions(path: ''),
                message: parsed?['detail'] as String? ?? 'Analysis failed',
              );
            }
          }
        }
      }
    }

    if (finalResult != null) {
      return AnalysisResult.fromJson(finalResult);
    }
    throw DioException(
      requestOptions: RequestOptions(path: ''),
      message: 'No result received from SSE stream',
    );
  }

  Map<String, dynamic>? _parseJson(String text) {
    try {
      return Map<String, dynamic>.from(
        (const JsonDecoder().convert(text)) as Map,
      );
    } catch (_) {
      return null;
    }
  }

}
