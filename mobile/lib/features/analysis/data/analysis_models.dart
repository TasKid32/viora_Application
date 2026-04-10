/// Skill extracted from CV analysis.
class Skill {
  final String name;
  final int proficiency;
  final String? category;

  const Skill({required this.name, required this.proficiency, this.category});

  factory Skill.fromJson(Map<String, dynamic> json) => Skill(
    name: json['name'] as String,
    proficiency: (json['proficiency'] as num).toInt(),
    category: json['category'] as String?,
  );
}

/// Missing skill identified by O*NET gap analysis.
class MissingSkill {
  final String skill;
  final String priority;
  final String? reason;
  final String type;  // 'tech', 'hard', 'soft'

  const MissingSkill({required this.skill, required this.priority, this.reason, this.type = 'hard'});

  factory MissingSkill.fromJson(Map<String, dynamic> json) => MissingSkill(
    skill: json['skill'] as String,
    priority: json['priority'] as String? ?? 'Medium',
    reason: json['reason'] as String?,
    type: json['type'] as String? ?? 'hard',
  );
}

/// Full analysis result from Backend.
class AnalysisResult {
  final String analysisId;
  final String predictedJob;
  final String experienceLevel;
  final String careerDirection;
  final List<Skill> strongSkills;
  final List<MissingSkill> missingSkills;
  final List<String> recommendations;
  final List<String> jobOpportunities;
  final Map<String, dynamic>? cvQuality;
  final List<String> languages;
  final List<String> extractedSkills;

  const AnalysisResult({
    required this.analysisId,
    required this.predictedJob,
    required this.experienceLevel,
    this.careerDirection = '',
    required this.strongSkills,
    required this.missingSkills,
    required this.recommendations,
    required this.jobOpportunities,
    this.cvQuality,
    this.languages = const [],
    this.extractedSkills = const [],
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    // Parse strong skills
    final rawSkills = json['user_profile']?['strong_skills'] ?? json['strong_skills'] ?? [];
    final strongSkills = (rawSkills as List).map((s) {
      if (s is Map<String, dynamic>) return Skill.fromJson(s);
      return Skill(name: s.toString(), proficiency: 75);
    }).toList();

    // Parse missing skills — TECH SKILLS first (specific tools), then generic
    final rawGap = json['gap_analysis'] ?? {};

    // Priority 1: Tech skills (Docker, AWS, EHR, Adobe, etc.)
    final rawTech = rawGap['missing_tech_skills'] ?? [];
    final techSkills = (rawTech as List).map((s) {
      if (s is Map<String, dynamic>) {
        return MissingSkill(
          skill: s['skill'] as String? ?? '',
          priority: s['priority'] as String? ?? 'Medium',
          reason: s['category'] as String?,
          type: 'tech',
        );
      }
      return MissingSkill(skill: s.toString(), priority: 'Medium', type: 'tech');
    }).toList();

    // Priority 2: Generic missing skills (from O*NET)
    final rawMissing = rawGap['missing_skills'] ?? json['missing_skills'] ?? [];
    // Determine type from gap_analysis lists
    final softSkillNames = (rawGap['missing_soft_skills'] as List?)?.map((s) => s.toString().toLowerCase()).toSet() ?? {};

    final genericSkills = (rawMissing as List).map((s) {
      if (s is Map<String, dynamic>) {
        final name = (s['skill'] as String? ?? '').toLowerCase();
        final type = softSkillNames.contains(name) ? 'soft' : 'hard';
        return MissingSkill(
          skill: s['skill'] as String? ?? '',
          priority: s['priority'] as String? ?? 'Medium',
          reason: s['reason'] as String?,
          type: type,
        );
      }
      return MissingSkill(skill: s.toString(), priority: 'Medium');
    }).toList();

    // Merge: tech first, then generic (avoid duplicates)
    final techNames = techSkills.map((t) => t.skill.toLowerCase()).toSet();
    final filteredGeneric = genericSkills
        .where((g) => !techNames.contains(g.skill.toLowerCase()))
        .toList();
    final missingSkills = [...techSkills, ...filteredGeneric];

    // Parse recommendations (structured JSON or plain strings)
    final rawRecs = json['recommendations'] ?? [];
    final recommendations = (rawRecs as List).map((r) {
      if (r is Map<String, dynamic>) {
        // Structured recommendation from backend
        final type = r['type'] ?? 'learn';
        final skill = r['skill'] ?? '';
        final priority = r['priority'] ?? 'Medium';
        final targetJob = r['target_job'] ?? '';
        final prefix = type == 'develop' ? 'Develop skill:' : 'Learn';
        final priorityEn = priority == 'High' ? 'High priority' :
                           priority == 'Medium' ? 'Medium priority' : 'Low priority';
        return '$prefix $skill — $priorityEn${targetJob.isNotEmpty ? ' for $targetJob' : ''}';
      }
      return r.toString();
    }).toList();

    // Parse job opportunities
    final rawJobs = json['job_opportunities'] ?? [];
    final jobOpportunities = (rawJobs as List).map((j) => j.toString()).toList();

    // Parse languages
    final rawLangs = json['languages'] ?? [];
    final languages = (rawLangs as List).map((l) => l.toString()).toList();

    // Parse career direction (O*NET occupation description)
    final careerDirection = json['user_profile']?['career_direction'] as String? ?? '';

    // Parse extracted skills (all skills NER found — for "show all" feature)
    final rawExtracted = json['user_profile']?['extracted_skills'] ?? [];
    final extractedSkills = (rawExtracted as List).map((s) => s.toString()).toList();

    return AnalysisResult(
      analysisId: json['analysis_id'] as String? ?? '',
      predictedJob: rawGap['predicted_job'] ?? json['predicted_job'] ?? 'Professional',
      experienceLevel: rawGap['experience_level'] ?? json['experience_level'] ?? 'Mid-Level',
      careerDirection: careerDirection,
      strongSkills: strongSkills,
      missingSkills: missingSkills,
      recommendations: recommendations,
      jobOpportunities: jobOpportunities,
      cvQuality: json['cv_quality'] as Map<String, dynamic>?,
      languages: languages,
      extractedSkills: extractedSkills,
    );
  }
}
