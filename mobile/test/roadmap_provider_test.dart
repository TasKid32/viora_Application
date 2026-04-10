import 'package:flutter_test/flutter_test.dart';
import 'package:viora_app/features/roadmap/data/roadmap_api.dart';

/// Tests for RoadmapPhase completed state and RoadmapData.hasRoadmap logic.
///
/// NOTE: Full provider integration tests (with mocked ApiClient) require
/// packages like `mockito` or `mocktail`. These unit tests verify
/// the data model behavior and state logic without network dependencies.
void main() {
  group('RoadmapPhase completed toggle', () {
    test('starts as not completed', () {
      final phase = RoadmapPhase(
        phase: 'Phase 1',
        duration: '4 weeks',
        priority: 'High',
        topics: [],
      );

      expect(phase.completed, false);
    });

    test('can toggle completed state', () {
      final phase = RoadmapPhase(
        phase: 'Phase 1',
        duration: '4 weeks',
        priority: 'High',
        topics: [],
      
      );

      phase.completed = true;
      expect(phase.completed, true);

      phase.completed = false;
      expect(phase.completed, false);
    });
  });

  group('RoadmapData hasRoadmap logic', () {
    test('empty phases means no roadmap', () {
      final data = RoadmapData.fromJson({'roadmap_id': 'x', 'learning_roadmap': []});
      expect(data.phases.isEmpty, true);
    });

    test('non-empty phases means has roadmap', () {
      final data = RoadmapData.fromJson({
        'roadmap_id': 'x',
        'learning_roadmap': [
          {'phase': 'P1', 'duration': '1w', 'priority': 'High', 'topics': ['A'], 'resources': []},
        ],
      });
      expect(data.phases.isNotEmpty, true);
      expect(data.phases.length, 1);
    });
  });

  group('RoadmapPhase optimistic rollback simulation', () {
    test('rollback restores original state', () {
      final phase = RoadmapPhase(
        phase: 'Phase 1',
        duration: '4 weeks',
        priority: 'High',
        topics: [],
        
      );

      // Simulate optimistic update
      final originalState = phase.completed;
      phase.completed = !phase.completed;
      expect(phase.completed, true);

      // Simulate rollback on error
      phase.completed = originalState;
      expect(phase.completed, false);
    });

    test('double toggle returns to original', () {
      final phase = RoadmapPhase(
        phase: 'Phase 1',
        duration: '4 weeks',
        priority: 'High',
        topics: [],
        
      );

      phase.completed = !phase.completed;
      phase.completed = !phase.completed;
      expect(phase.completed, false); // Back to original
    });
  });
}
