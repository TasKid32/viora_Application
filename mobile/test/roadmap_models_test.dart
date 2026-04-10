import 'package:flutter_test/flutter_test.dart';
import 'package:viora_app/features/roadmap/data/roadmap_api.dart';

void main() {
  group('LearningResource', () {
    test('fromJson parses correctly', () {
      final json = {
        'title': 'Python Crash Course',
        'url': 'https://youtube.com/watch?v=123',
        'platform': 'YouTube',
        'thumbnail': 'https://img.youtube.com/vi/123/default.jpg',
      };
      final resource = LearningResource.fromJson(json);

      expect(resource.title, 'Python Crash Course');
      expect(resource.url, 'https://youtube.com/watch?v=123');
      expect(resource.platform, 'YouTube');
      expect(resource.thumbnail, 'https://img.youtube.com/vi/123/default.jpg');
      expect(resource.completed, false); // default
    });

    test('fromJson parses completed=true', () {
      final json = {
        'title': 'Docker Course',
        'url': 'https://udemy.com/docker',
        'platform': 'Udemy',
        'completed': true,
      };
      final resource = LearningResource.fromJson(json);
      expect(resource.completed, true);
    });

    test('completed can be toggled', () {
      final resource = LearningResource(title: 'Test', url: '', platform: 'Web', type: 'course');
      expect(resource.completed, false);
      resource.completed = true;
      expect(resource.completed, true);
    });

    test('fromJson defaults platform to Web', () {
      final json = {'title': 'Test'};
      final resource = LearningResource.fromJson(json);

      expect(resource.platform, 'Web');
      expect(resource.title, 'Test');
      expect(resource.url, '');
      expect(resource.thumbnail, isNull);
    });
  });

  group('RoadmapPhase', () {
    test('fromJson parses complete phase', () {
      final json = {
        'phase': 'Foundations',
        'duration': '4 weeks',
        'priority': 'High',
        'topics': ['Docker', 'Kubernetes', 'CI/CD'],
        'resources': [
          {'title': 'Docker Tutorial', 'url': 'https://yt.com/1', 'platform': 'YouTube'},
          {'title': 'K8s Course', 'url': 'https://udemy.com/1', 'platform': 'Udemy'},
        ],
        'completed': false,
      };
      final phase = RoadmapPhase.fromJson(json);

      expect(phase.phase, 'Foundations');
      expect(phase.duration, '4 weeks');
      expect(phase.priority, 'High');
      expect(phase.topics, ['Docker', 'Kubernetes', 'CI/CD']);
      expect(phase.resources.length, 2);
      expect(phase.resources[0].title, 'Docker Tutorial');
      expect(phase.resources[1].platform, 'Udemy');
      expect(phase.completed, false);
    });

    test('fromJson handles empty resources', () {
      final json = {
        'phase': 'Advanced',
        'duration': '2 weeks',
        'priority': 'Low',
        'topics': ['Systems Analysis'],
      };
      final phase = RoadmapPhase.fromJson(json);

      expect(phase.resources, isEmpty);
      expect(phase.completed, false); // Default
    });

    test('fromJson handles null values', () {
      final json = <String, dynamic>{};
      final phase = RoadmapPhase.fromJson(json);

      expect(phase.phase, '');
      expect(phase.duration, '');
      expect(phase.priority, 'Medium');
      expect(phase.topics, isEmpty);
      expect(phase.resources, isEmpty);
    });

    test('completed can be toggled', () {
      final phase = RoadmapPhase(
        phase: 'Test',
        duration: '1 week',
        priority: 'High',
        topics: [],
        
      );

      expect(phase.completed, false);
      phase.completed = true;
      expect(phase.completed, true);
    });
  });

  group('RoadmapData', () {
    test('fromJson parses complete roadmap', () {
      final json = {
        'roadmap_id': 'rm-1',
        'learning_roadmap': [
          {
            'phase': 'Phase 1',
            'duration': '4 weeks',
            'priority': 'High',
            'topics': ['Topic 1'],
            'resources': [],
          },
          {
            'phase': 'Phase 2',
            'duration': '2 weeks',
            'priority': 'Medium',
            'topics': ['Topic 2'],
            'resources': [],
          },
        ],
      };
      final data = RoadmapData.fromJson(json);

      expect(data.roadmapId, 'rm-1');
      expect(data.phases.length, 2);
      expect(data.phases[0].phase, 'Phase 1');
      expect(data.phases[1].priority, 'Medium');
    });

    test('fromJson handles empty roadmap', () {
      final json = <String, dynamic>{'roadmap_id': null};
      final data = RoadmapData.fromJson(json);

      expect(data.roadmapId, '');
      expect(data.phases, isEmpty);
    });

    test('fromJson with real backend response shape', () {
      // Simulate actual backend response from roadmap endpoint
      final json = {
        'roadmap_id': '550e8400-e29b-41d4-a716-446655440000',
        'learning_roadmap': [
          {
            'phase': 'Foundations',
            'duration': '4 weeks',
            'priority': 'High',
            'topics': ['Apache Kafka', 'Go', 'Eclipse IDE'],
            'resources': [
              {'title': 'Kafka for Beginners', 'url': 'https://youtube.com/w', 'platform': 'YouTube', 'thumbnail': 'https://i.ytimg.com/vi/x.jpg'},
              {'title': 'Go Complete Guide', 'url': 'https://www.udemy.com/course/go', 'platform': 'Udemy'},
            ],
          },
        ],
      };
      final data = RoadmapData.fromJson(json);

      expect(data.phases.first.topics, contains('Apache Kafka'));
      expect(data.phases.first.resources.length, 2);
      expect(data.phases.first.resources[0].platform, 'YouTube');
      expect(data.phases.first.resources[1].thumbnail, isNull);
    });
  });
}
