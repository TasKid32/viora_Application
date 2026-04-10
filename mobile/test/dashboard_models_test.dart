import 'package:flutter_test/flutter_test.dart';
import 'package:viora_app/features/dashboard/data/dashboard_api.dart';

void main() {
  group('DashboardData.fromJson', () {
    test('parses complete response', () {
      final json = {
        'user': {
          'name': 'Salman Ahmed',
          'email': 'salman@test.com',
          'profile_picture': 'https://cdn.test/avatar.jpg',
        },
        'progress': {
          'overall_percentage': 65,
          'skill_growth': 12,
          'has_analysis': true,
          'has_roadmap': true,
          'total_courses': 10,
          'completed_courses_count': 3,
          'roadmap_steps_total': 5,
          'roadmap_steps_completed': 2,
          'roadmap_resources_total': 15,
          'roadmap_resources_completed': 7,
        },
        'notifications_count': 4,
      };
      final data = DashboardData.fromJson(json);

      expect(data.userName, 'Salman Ahmed');
      expect(data.userEmail, 'salman@test.com');
      expect(data.avatarUrl, 'https://cdn.test/avatar.jpg');
      expect(data.overallProgress, 65);
      expect(data.skillGrowth, 12);
      expect(data.hasAnalysis, true);
      expect(data.hasRoadmap, true);
      expect(data.totalCourses, 10);
      expect(data.completedCourses, 3);
      expect(data.notificationsCount, 4);
      expect(data.roadmapStepsTotal, 5);
      expect(data.roadmapStepsCompleted, 2);
      expect(data.roadmapResourcesTotal, 15);
      expect(data.roadmapResourcesCompleted, 7);
    });

    test('handles empty/missing fields with defaults', () {
      final json = <String, dynamic>{};
      final data = DashboardData.fromJson(json);

      expect(data.userName, 'User');
      expect(data.userEmail, '');
      expect(data.avatarUrl, isNull);
      expect(data.overallProgress, 0);
      expect(data.skillGrowth, 0);
      expect(data.hasAnalysis, false);
      expect(data.hasRoadmap, false);
      expect(data.totalCourses, 0);
      expect(data.completedCourses, 0);
      expect(data.notificationsCount, 0);
      expect(data.roadmapStepsTotal, 0);
      expect(data.roadmapStepsCompleted, 0);
      expect(data.roadmapResourcesTotal, 0);
      expect(data.roadmapResourcesCompleted, 0);
    });

    test('handles null user map', () {
      final json = {'user': null, 'progress': null};
      final data = DashboardData.fromJson(json);

      expect(data.userName, 'User');
      expect(data.overallProgress, 0);
    });

    test('handles new user (no analysis, no roadmap)', () {
      final json = {
        'user': {'name': 'New User', 'email': 'new@test.com'},
        'progress': {
          'overall_percentage': 0,
          'has_analysis': false,
          'has_roadmap': false,
        },
      };
      final data = DashboardData.fromJson(json);

      expect(data.hasAnalysis, false);
      expect(data.hasRoadmap, false);
      expect(data.overallProgress, 0);
    });
  });
}
