import 'package:flutter_test/flutter_test.dart';
import 'package:viora_app/features/analysis/data/analysis_models.dart';

void main() {
  group('Skill', () {
    test('fromJson parses correctly', () {
      final json = {'name': 'Python', 'proficiency': 85, 'category': 'Programming'};
      final skill = Skill.fromJson(json);

      expect(skill.name, 'Python');
      expect(skill.proficiency, 85);
      expect(skill.category, 'Programming');
    });

    test('fromJson handles null category', () {
      final json = {'name': 'SQL', 'proficiency': 70};
      final skill = Skill.fromJson(json);

      expect(skill.name, 'SQL');
      expect(skill.proficiency, 70);
      expect(skill.category, isNull);
    });

    test('fromJson handles double proficiency', () {
      final json = {'name': 'Git', 'proficiency': 75.5};
      final skill = Skill.fromJson(json);

      expect(skill.proficiency, 75); // toInt() truncates
    });
  });

  group('MissingSkill', () {
    test('fromJson parses correctly', () {
      final json = {'skill': 'Docker', 'priority': 'High', 'reason': 'Required for DevOps'};
      final ms = MissingSkill.fromJson(json);

      expect(ms.skill, 'Docker');
      expect(ms.priority, 'High');
      expect(ms.reason, 'Required for DevOps');
    });

    test('fromJson defaults priority to Medium', () {
      final json = {'skill': 'AWS'};
      final ms = MissingSkill.fromJson(json);

      expect(ms.skill, 'AWS');
      expect(ms.priority, 'Medium');
      expect(ms.reason, isNull);
    });
  });

  group('AnalysisResult.fromJson', () {
    test('parses complete backend response (Salman CV format)', () {
      final json = _fullBackendResponse();
      final result = AnalysisResult.fromJson(json);

      expect(result.analysisId, 'abc123');
      expect(result.predictedJob, 'Computer and Information Research Scientists');
      expect(result.experienceLevel, 'Mid-Level');
      expect(result.strongSkills.length, greaterThan(0));
      expect(result.missingSkills.length, greaterThan(0));
      expect(result.recommendations.length, greaterThan(0));
      expect(result.jobOpportunities.length, greaterThan(0));
      expect(result.languages, contains('Arabic'));
      expect(result.languages, contains('English'));
    });

    test('tech skills appear BEFORE generic missing skills', () {
      final json = _fullBackendResponse();
      final result = AnalysisResult.fromJson(json);

      // Tech skills should be first in missingSkills list
      final firstMissing = result.missingSkills.first;
      expect(firstMissing.skill, 'Apache Kafka'); // Tech skill
      expect(firstMissing.reason, 'Development environment software'); // Category as reason
    });

    test('deduplicates tech and generic skills', () {
      final json = _responseWithDuplicateSkills();
      final result = AnalysisResult.fromJson(json);

      // 'Docker' appears in both tech and generic — should appear once
      final dockerSkills = result.missingSkills.where((s) => s.skill == 'Docker').toList();
      expect(dockerSkills.length, 1);
    });

    test('parses strong skills from user_profile.strong_skills', () {
      final json = _fullBackendResponse();
      final result = AnalysisResult.fromJson(json);

      expect(result.strongSkills.any((s) => s.name == 'Python'), isTrue);
      expect(result.strongSkills.first.proficiency, 75);
    });

    test('handles strong skills as plain strings', () {
      final json = {
        'analysis_id': 'test1',
        'strong_skills': ['Python', 'Java', 'SQL'], // Plain strings
        'gap_analysis': {'predicted_job': 'Developer', 'experience_level': 'Junior'},
      };
      final result = AnalysisResult.fromJson(json);

      expect(result.strongSkills.length, 3);
      expect(result.strongSkills[0].name, 'Python');
      expect(result.strongSkills[0].proficiency, 75); // Default
    });

    test('parses structured recommendations', () {
      final json = _fullBackendResponse();
      final result = AnalysisResult.fromJson(json);

      // Structured recommendations are converted to readable strings
      expect(result.recommendations.first, contains('Apache Kafka'));
      expect(result.recommendations.first, contains('High priority'));
    });

    test('handles plain string recommendations', () {
      final json = {
        'analysis_id': 'test2',
        'gap_analysis': {'predicted_job': 'Dev'},
        'recommendations': ['Learn Docker', 'Practice SQL'],
      };
      final result = AnalysisResult.fromJson(json);

      expect(result.recommendations, equals(['Learn Docker', 'Practice SQL']));
    });

    test('handles empty/missing fields gracefully', () {
      final json = <String, dynamic>{'analysis_id': null, 'gap_analysis': null};
      final result = AnalysisResult.fromJson(json);

      expect(result.analysisId, '');
      expect(result.predictedJob, 'Professional'); // Default
      expect(result.experienceLevel, 'Mid-Level'); // Default
      expect(result.strongSkills, isEmpty);
      expect(result.missingSkills, isEmpty);
      expect(result.recommendations, isEmpty);
      expect(result.jobOpportunities, isEmpty);
      expect(result.languages, isEmpty);
    });

    test('handles completely empty JSON', () {
      final json = <String, dynamic>{};
      final result = AnalysisResult.fromJson(json);

      expect(result.analysisId, '');
      expect(result.predictedJob, 'Professional');
      expect(result.experienceLevel, 'Mid-Level');
    });

    test('parses cv_quality map', () {
      final json = {
        'analysis_id': 'q1',
        'gap_analysis': {'predicted_job': 'Dev'},
        'cv_quality': {
          'score': 85,
          'is_valid': true,
          'word_count': 500,
          'found_sections': ['Summary', 'Skills'],
          'missing_sections': ['Certificates'],
        },
      };
      final result = AnalysisResult.fromJson(json);

      expect(result.cvQuality, isNotNull);
      expect(result.cvQuality!['score'], 85);
      expect(result.cvQuality!['is_valid'], true);
    });

    test('parses predictedJob from gap_analysis over top-level', () {
      final json = {
        'analysis_id': 'p1',
        'predicted_job': 'Generic Dev',
        'gap_analysis': {'predicted_job': 'Software Developers'},
      };
      final result = AnalysisResult.fromJson(json);

      // gap_analysis.predicted_job should take priority
      expect(result.predictedJob, 'Software Developers');
    });

    test('falls back to top-level predicted_job when gap_analysis missing', () {
      final json = {
        'analysis_id': 'p2',
        'predicted_job': 'Data Scientist',
      };
      final result = AnalysisResult.fromJson(json);

      expect(result.predictedJob, 'Data Scientist');
    });
  });
}

// ─── Test data helpers ──────────────────────────────────────

Map<String, dynamic> _fullBackendResponse() {
  return {
    'analysis_id': 'abc123',
    'user_profile': {
      'strong_skills': [
        {'name': 'Python', 'proficiency': 75, 'category': 'Programming'},
        {'name': 'Django', 'proficiency': 80, 'category': 'Framework'},
        {'name': 'SQL', 'proficiency': 70},
      ],
    },
    'gap_analysis': {
      'predicted_job': 'Computer and Information Research Scientists',
      'experience_level': 'Mid-Level',
      'missing_skills': [
        {'skill': 'Systems Analysis', 'priority': 'Medium'},
        {'skill': 'Critical Thinking', 'priority': 'High'},
      ],
      'missing_tech_skills': [
        {'skill': 'Apache Kafka', 'priority': 'High', 'category': 'Development environment software', 'hot_technology': true},
        {'skill': 'Go', 'priority': 'High', 'category': 'Development environment software', 'hot_technology': true},
      ],
    },
    'recommendations': [
      {'type': 'learn', 'skill': 'Apache Kafka', 'priority': 'High', 'target_job': 'Researcher'},
      {'type': 'develop', 'skill': 'Systems Analysis', 'priority': 'Medium', 'target_job': ''},
    ],
    'job_opportunities': [
      'Computer and Information Research Scientists',
      'Software Developers',
      'Web Developers',
    ],
    'languages': ['Arabic', 'English'],
    'cv_quality': {'score': 80, 'is_valid': true, 'word_count': 600},
  };
}

Map<String, dynamic> _responseWithDuplicateSkills() {
  return {
    'analysis_id': 'dup1',
    'gap_analysis': {
      'predicted_job': 'DevOps',
      'experience_level': 'Junior',
      'missing_skills': [
        {'skill': 'Docker', 'priority': 'High'},
        {'skill': 'Linux', 'priority': 'Medium'},
      ],
      'missing_tech_skills': [
        {'skill': 'Docker', 'priority': 'High', 'category': 'Container'},
        {'skill': 'Kubernetes', 'priority': 'High', 'category': 'Container'},
      ],
    },
  };
}
