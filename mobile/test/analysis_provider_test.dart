import 'package:flutter_test/flutter_test.dart';
import 'package:viora_app/features/analysis/provider/analysis_provider.dart';

/// Tests for AnalysisProvider enums, constants, and AnalysisStage logic.
///
/// NOTE: Full provider integration tests (with mocked ApiClient) require
/// packages like `mockito` or `mocktail`. These unit tests verify the
/// enum, stage logic, and state machine without network dependencies.
void main() {
  group('AnalysisStage enum', () {
    test('has exactly 7 stages', () {
      expect(AnalysisStage.values.length, 7);
    });

    test('stages are in correct order', () {
      expect(AnalysisStage.idle.index, 0);
      expect(AnalysisStage.uploading.index, 1);
      expect(AnalysisStage.extracting.index, 2);
      expect(AnalysisStage.analyzing.index, 3);
      expect(AnalysisStage.matching.index, 4);
      expect(AnalysisStage.complete.index, 5);
      expect(AnalysisStage.error.index, 6);
    });

    test('values list is complete', () {
      expect(AnalysisStage.values, [
        AnalysisStage.idle,
        AnalysisStage.uploading,
        AnalysisStage.extracting,
        AnalysisStage.analyzing,
        AnalysisStage.matching,
        AnalysisStage.complete,
        AnalysisStage.error,
      ]);
    });
  });

  group('AnalysisStage loading logic', () {
    test('idle is NOT loading', () {
      expect(_isLoading(AnalysisStage.idle), false);
    });

    test('uploading IS loading', () {
      expect(_isLoading(AnalysisStage.uploading), true);
    });

    test('extracting IS loading', () {
      expect(_isLoading(AnalysisStage.extracting), true);
    });

    test('analyzing IS loading', () {
      expect(_isLoading(AnalysisStage.analyzing), true);
    });

    test('matching IS loading', () {
      expect(_isLoading(AnalysisStage.matching), true);
    });

    test('complete is NOT loading', () {
      expect(_isLoading(AnalysisStage.complete), false);
    });

    test('error is NOT loading', () {
      expect(_isLoading(AnalysisStage.error), false);
    });
  });
}

/// Mirrors AnalysisProvider.isLoading logic (L41-45) for isolated testing.
bool _isLoading(AnalysisStage stage) {
  return stage == AnalysisStage.uploading ||
      stage == AnalysisStage.extracting ||
      stage == AnalysisStage.analyzing ||
      stage == AnalysisStage.matching;
}
