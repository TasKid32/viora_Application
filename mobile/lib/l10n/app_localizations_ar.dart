// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Arabic (`ar`).
class AppLocalizationsAr extends AppLocalizations {
  AppLocalizationsAr([String locale = 'ar']) : super(locale);

  @override
  String get appName => 'فيورا';

  @override
  String get appTagline => 'معاً نصنع رؤيتك.';

  @override
  String get appDeveloper => 'تم تطويرة بواسطة فريق فورا - جامعة الجوف ©2026';

  @override
  String get getStarted => 'ابدأ الآن';

  @override
  String get welcomeBack => 'مرحباً بك في فيورا ';

  @override
  String get signInToContinue => 'سجل الدخول للمتابعة';

  @override
  String get email => 'البريد الإلكتروني';

  @override
  String get emailHint => 'you@example.com';

  @override
  String get password => 'كلمة المرور';

  @override
  String get signIn => 'تسجيل الدخول';

  @override
  String get dontHaveAccount => 'ليس لديك حساب؟ ';

  @override
  String get signUp => 'إنشاء حساب';

  @override
  String get pleaseEnterEmail => 'يرجى إدخال البريد الإلكتروني';

  @override
  String get pleaseEnterValidEmail => 'يرجى إدخال بريد إلكتروني صحيح';

  @override
  String get pleaseEnterPassword => 'يرجى إدخال كلمة المرور';

  @override
  String get passwordMinLength =>
      'يجب أن تحتوي كلمة المرور على 8 خانات، تشمل حرفاً كبيراً، وصغيراً، ورقماً، ورمزاً خاصاً';

  @override
  String get joinViora => 'انضم إلى فيورا';

  @override
  String get startCareerJourney => 'ابدأ رحلتك المهنية اليوم';

  @override
  String get fullName => 'الاسم الكامل';

  @override
  String get fullNameHint => 'تسنيم النشمي';

  @override
  String get confirmPassword => 'تأكيد كلمة المرور';

  @override
  String get createAccount => 'إنشاء حساب';

  @override
  String get alreadyHaveAccount => 'لديك حساب بالفعل؟ ';

  @override
  String get logIn => 'تسجيل الدخول';

  @override
  String get pleaseEnterName => 'يرجى إدخال اسمك';

  @override
  String get pleaseConfirmPassword => 'يرجى تأكيد كلمة المرور';

  @override
  String get passwordsDoNotMatch => 'كلمات المرور غير متطابقة';

  @override
  String get forgotPasswordTitle => 'نسيت كلمة المرور؟';

  @override
  String get forgotPasswordDescription =>
      'لا تقلق! أدخل بريدك الإلكتروني وسنرسل لك رابطاً لإعادة تعيين كلمة المرور.';

  @override
  String get emailAddress => 'البريد الإلكتروني';

  @override
  String get enterYourEmail => 'أدخل بريدك الإلكتروني';

  @override
  String get sendResetLink => 'إرسال رابط الإعادة';

  @override
  String get backToSignIn => 'العودة لتسجيل الدخول';

  @override
  String get checkYourEmail => 'تحقق من بريدك';

  @override
  String get resetLinkSent => 'لقد أرسلنا رابط إعادة تعيين كلمة المرور إلى:';

  @override
  String get didntReceiveEmail => 'لم تستلم البريد؟';

  @override
  String get checkSpamOrRetry =>
      'تحقق من مجلد البريد العشوائي أو حاول مرة أخرى';

  @override
  String get resendEmail => 'إعادة إرسال البريد';

  @override
  String get resetLinkSentSuccess => 'تم إرسال رابط إعادة التعيين بنجاح!';

  @override
  String failedToSendResetLink(String error) {
    return 'فشل في إرسال رابط الإعادة: $error';
  }

  @override
  String hello(String name) {
    return 'مرحباً، $name ';
  }

  @override
  String get readyToGrow => 'مستعد لتطوير مهاراتك اليوم؟';

  @override
  String get yourProgress => 'تقدمك';

  @override
  String get retry => 'إعادة المحاولة';

  @override
  String get skillAnalysis => 'تحليل المهارات';

  @override
  String get careerPath => 'المسار المهني';

  @override
  String get training => 'التدريب';

  @override
  String get smartAssistant => 'المساعد الذكي';

  @override
  String get myCourses => 'دوراتي';

  @override
  String coursesCount(int count) {
    return '$count دورة';
  }

  @override
  String get searchCourses => 'بحث في الدورات...';

  @override
  String get all => 'الكل';

  @override
  String get inProgress => 'قيد التقدم';

  @override
  String get completed => 'مكتملة';

  @override
  String get failedToLoadCourses => 'فشل في تحميل الدورات';

  @override
  String get unknownError => 'خطأ غير معروف';

  @override
  String get noCoursesFound => 'لا توجد دورات';

  @override
  String get addFirstCourse => 'أضف أول دورة لك للبدء';

  @override
  String get continueLearning => 'متابعة التعلم';

  @override
  String get edit => 'تعديل';

  @override
  String get delete => 'حذف';

  @override
  String get addNewCourse => 'إضافة دورة جديدة';

  @override
  String get courseTitle => 'عنوان الدورة';

  @override
  String get category => 'الفئة';

  @override
  String get platform => 'المنصة';

  @override
  String get cancel => 'إلغاء';

  @override
  String get add => 'إضافة';

  @override
  String get updateProgress => 'تحديث التقدم';

  @override
  String get completionPercent => 'نسبة الإنجاز (%)';

  @override
  String get update => 'تحديث';

  @override
  String get deleteCourse => 'حذف الدورة';

  @override
  String deleteCourseConfirmation(String title) {
    return 'هل أنت متأكد من حذف \"$title\"؟';
  }

  @override
  String get failedToLoadCourse => 'فشل في تحميل الدورة';

  @override
  String get courseNotFound => 'الدورة غير موجودة';

  @override
  String get enrolled => 'مسجل';

  @override
  String get notEnrolled => 'غير مسجل';

  @override
  String get courseProgress => 'تقدم الدورة';

  @override
  String get courseDetails => 'تفاصيل الدورة';

  @override
  String get title => 'العنوان';

  @override
  String get status => 'الحالة';

  @override
  String get markAsCompleted => 'تحديد كمكتملة';

  @override
  String get notStarted => 'لم تبدأ';

  @override
  String get uploadCV => 'ارفع سيرتك الذاتية';

  @override
  String get uploadCVDesc => 'ارفع سيرتك الذاتية لتحليل مهاراتك';

  @override
  String get selectFile => 'اختر ملف';

  @override
  String get uploadAndAnalyze => 'رفع وتحليل';

  @override
  String get analyzing => 'جاري التحليل...';

  @override
  String get analysisComplete => 'اكتمل التحليل';

  @override
  String get yourSkills => 'مهاراتك';

  @override
  String get generateRoadmap => 'إنشاء خطة تعلم';

  @override
  String get noSkillsFound => 'لم يتم العثور على مهارات';

  @override
  String get pleaseUploadCV => 'يرجى رفع سيرتك الذاتية أولاً';

  @override
  String get analysisInProgress => 'التحليل قيد التنفيذ...';

  @override
  String get pleaseWait => 'يرجى الانتظار أثناء تحليل سيرتك الذاتية';

  @override
  String skillsFound(int count) {
    return 'تم العثور على $count مهارة';
  }

  @override
  String get manualSkillEntry => 'أو أدخل المهارات يدوياً';

  @override
  String get enterSkill => 'أدخل مهارة';

  @override
  String get addSkill => 'إضافة مهارة';

  @override
  String get submitSkills => 'إرسال المهارات';

  @override
  String get trackYourProgress => 'تقدمك';

  @override
  String get trackLearningJourney => 'تتبع رحلة تعلمك';

  @override
  String get skillGrowth => 'نمو المهارات';

  @override
  String get weeklyActivity => 'النشاط الأسبوعي';

  @override
  String get noActivityData => 'لا توجد بيانات نشاط';

  @override
  String get completedCourses => 'الدورات المكتملة';

  @override
  String get noCompletedCourses => 'لا توجد دورات مكتملة بعد';

  @override
  String get notifications => 'الإشعارات';

  @override
  String newNotificationsCount(int count) {
    return '$count إشعار جديد';
  }

  @override
  String get markAllRead => 'قراءة الكل';

  @override
  String get noNotificationsYet => 'لا توجد إشعارات بعد';

  @override
  String get notificationsEmptyDesc =>
      'ستظهر الإشعارات هنا عندما يكون لديك تحديثات';

  @override
  String get notificationDeleted => 'تم حذف الإشعار';

  @override
  String get failedToLoadNotifications => 'فشل في تحميل الإشعارات';

  @override
  String get failedToMarkAsRead => 'فشل في تحديد كمقروء';

  @override
  String get failedToDeleteNotification => 'فشل في حذف الإشعار';

  @override
  String get allMarkedAsRead => 'تم تحديد جميع الإشعارات كمقروءة';

  @override
  String get failedToMarkAllRead => 'فشل في تحديد الكل كمقروء';

  @override
  String get justNow => 'الآن';

  @override
  String minutesAgo(int count) {
    return 'منذ $count دقيقة';
  }

  @override
  String hoursAgo(int count) {
    return 'منذ $count ساعة';
  }

  @override
  String get yesterday => 'أمس';

  @override
  String daysAgo(int count) {
    return 'منذ $count يوم';
  }

  @override
  String unreadNotifications(int count) {
    return 'لديك $count إشعار غير مقروء';
  }

  @override
  String get stayUpdated => 'ابق على اطلاع بتقدمك';

  @override
  String get settings => 'الإعدادات';

  @override
  String get manageAccount => 'إدارة حسابك';

  @override
  String get editProfile => 'تعديل الملف الشخصي';

  @override
  String get updateYourInfo => 'تحديث معلوماتك';

  @override
  String get notificationSettings => 'الإشعارات';

  @override
  String get manageAlerts => 'إدارة التنبيهات';

  @override
  String get privacySecurity => 'الخصوصية والأمان';

  @override
  String get keepDataSafe => 'حافظ على أمان بياناتك';

  @override
  String get language => 'اللغة';

  @override
  String get arabic => 'العربية';

  @override
  String get english => 'الإنجليزية';

  @override
  String get helpSupport => 'المساعدة والدعم';

  @override
  String get getAssistance => 'احصل على المساعدة';

  @override
  String get loading => 'جاري التحميل...';

  @override
  String get failedToLoadProfile => 'فشل في تحميل الملف الشخصي';

  @override
  String get phone => 'الهاتف';

  @override
  String get bio => 'نبذة';

  @override
  String get saveChanges => 'حفظ التغييرات';

  @override
  String get profileUpdatedSuccess => 'تم تحديث الملف الشخصي بنجاح';

  @override
  String failedToUpdateProfile(String error) {
    return 'فشل في تحديث الملف الشخصي: $error';
  }

  @override
  String get changePassword => 'تغيير كلمة المرور';

  @override
  String get passwordMinLength8 =>
      'يجب أن تتكون كلمة المرور من 8 أحرف على الأقل';

  @override
  String get currentPassword => 'كلمة المرور الحالية';

  @override
  String get enterCurrentPassword => 'أدخل كلمة المرور الحالية';

  @override
  String get newPassword => 'كلمة المرور الجديدة';

  @override
  String get enterNewPassword => 'أدخل كلمة المرور الجديدة';

  @override
  String get confirmNewPassword => 'تأكيد كلمة المرور الجديدة';

  @override
  String get confirmNewPasswordHint => 'تأكيد كلمة المرور الجديدة';

  @override
  String get pleaseEnterCurrentPassword => 'يرجى إدخال كلمة المرور الحالية';

  @override
  String get pleaseEnterNewPassword => 'يرجى إدخال كلمة مرور جديدة';

  @override
  String get passwordMin8Chars => 'كلمة المرور يجب أن تكون 8 أحرف على الأقل';

  @override
  String get newPasswordMustDiffer =>
      'كلمة المرور الجديدة يجب أن تختلف عن الحالية';

  @override
  String get pleaseConfirmNewPassword => 'يرجى تأكيد كلمة المرور الجديدة';

  @override
  String get passwordChangedSuccess => 'تم تغيير كلمة المرور بنجاح!';

  @override
  String failedToChangePassword(String error) {
    return 'فشل في تغيير كلمة المرور: $error';
  }

  @override
  String get weak => 'ضعيفة';

  @override
  String get fair => 'مقبولة';

  @override
  String get good => 'جيدة';

  @override
  String get strong => 'قوية';

  @override
  String get atLeast8Chars => '8 أحرف على الأقل';

  @override
  String get containsUppercase => 'تحتوي على حرف كبير';

  @override
  String get containsLowercase => 'تحتوي على حرف صغير';

  @override
  String get containsNumber => 'تحتوي على رقم';

  @override
  String get selectLanguage => 'اختر اللغة';

  @override
  String get languageUpdatedSuccess => 'تم تحديث اللغة بنجاح';

  @override
  String get notificationSettingsTitle => 'إعدادات الإشعارات';

  @override
  String get general => 'عام';

  @override
  String get pushNotifications => 'إشعارات الدفع';

  @override
  String get receivePushNotifications => 'استقبال إشعارات الدفع';

  @override
  String get emailNotifications => 'إشعارات البريد';

  @override
  String get receiveEmailUpdates => 'استقبال تحديثات البريد';

  @override
  String get notificationTypes => 'أنواع الإشعارات';

  @override
  String get courseUpdates => 'تحديثات الدورات';

  @override
  String get newCoursesContent => 'دورات ومحتوى جديد';

  @override
  String get progressReports => 'تقارير التقدم';

  @override
  String get weeklyProgressSummary => 'ملخص التقدم الأسبوعي';

  @override
  String get achievements => 'الإنجازات';

  @override
  String get badgesAndRewards => 'الشارات والمكافآت';

  @override
  String get recommendations => 'التوصيات';

  @override
  String get personalizedSuggestions => 'اقتراحات مخصصة';

  @override
  String get security => 'الأمان';

  @override
  String get updateYourPassword => 'تحديث كلمة المرور';

  @override
  String get twoFactorAuth => 'المصادقة الثنائية';

  @override
  String get extraSecurityLayer => 'طبقة أمان إضافية';

  @override
  String get biometricLogin => 'تسجيل الدخول البيومتري';

  @override
  String get useFingerprintOrFace => 'استخدم البصمة أو الوجه';

  @override
  String get privacy => 'الخصوصية';

  @override
  String get profileVisibility => 'رؤية الملف الشخصي';

  @override
  String get whoCanSeeProfile => 'من يمكنه رؤية ملفك الشخصي';

  @override
  String get profileVisibilityComingSoon => 'إعدادات رؤية الملف الشخصي قريباً.';

  @override
  String get downloadMyData => 'تحميل بياناتي';

  @override
  String get getCopyOfData => 'احصل على نسخة من بياناتك';

  @override
  String get dataDownloadComingSoon => 'ميزة تحميل البيانات قريباً.';

  @override
  String get account => 'الحساب';

  @override
  String get logout => 'تسجيل الخروج';

  @override
  String get signOutOfAccount => 'تسجيل الخروج من حسابك';

  @override
  String get logoutConfirmation => 'هل أنت متأكد من تسجيل الخروج؟';

  @override
  String get deleteAccount => 'حذف الحساب';

  @override
  String get permanentlyDeleteAccount => 'حذف الحساب نهائياً';

  @override
  String get deleteAccountWarning =>
      'لا يمكن التراجع عن هذا الإجراء. سيتم حذف جميع بياناتك نهائياً.';

  @override
  String get accountDeletionNotAvailable => 'حذف الحساب غير متاح حالياً.';

  @override
  String get getHelp => 'احصل على المساعدة';

  @override
  String get faqs => 'الأسئلة الشائعة';

  @override
  String get frequentlyAskedQuestions => 'الأسئلة المتكررة';

  @override
  String get liveChat => 'الدردشة المباشرة';

  @override
  String get chatWithSupport => 'تحدث مع فريق الدعم';

  @override
  String get emailSupport => 'دعم البريد الإلكتروني';

  @override
  String get resources => 'الموارد';

  @override
  String get videoTutorials => 'دروس فيديو';

  @override
  String get learnHowToUse => 'تعلم كيفية استخدام فيورا';

  @override
  String get userGuide => 'دليل المستخدم';

  @override
  String get completeDocumentation => 'التوثيق الكامل';

  @override
  String get about => 'حول';

  @override
  String get aboutViora => 'حول فيورا';

  @override
  String get versionInfo => 'الإصدار 1.0.0';

  @override
  String get termsOfService => 'شروط الخدمة';

  @override
  String get readOurTerms => 'اقرأ شروطنا';

  @override
  String get privacyPolicy => 'سياسة الخصوصية';

  @override
  String get howWeProtectData => 'كيف نحمي بياناتك';

  @override
  String comingSoon(String feature) {
    return '$feature قريباً.';
  }

  @override
  String get aiAssistant => 'المساعد الذكي';

  @override
  String get askMeAnything => 'اسألني أي شيء عن مسيرتك المهنية...';

  @override
  String get typeMessage => 'اكتب رسالتك...';

  @override
  String get errorNetwork => 'حدث خطأ في الشبكة';

  @override
  String get errorServer => 'حدث خطأ في الخادم';

  @override
  String get errorUnauthorized => 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى';

  @override
  String get errorTimeout => 'انتهت مهلة الطلب';

  @override
  String get errorUnknown => 'حدث خطأ غير متوقع';

  @override
  String get languageUpdated => 'تم تحديث اللغة بنجاح';

  @override
  String get navHome => 'الرئيسية';

  @override
  String get navProgress => 'التقدم';

  @override
  String get navAssistant => 'المساعد';

  @override
  String get navProfile => 'الملف الشخصي';

  @override
  String get smartAssistantTitle => 'المساعد الذكي';

  @override
  String get alwaysHereToHelp => 'هنا دائماً لمساعدتك';

  @override
  String get quickActions => 'إجراءات سريعة:';

  @override
  String get analyzeCV => 'تحليل السيرة الذاتية';

  @override
  String get helpAnalyzeCV => 'ساعدني في تحليل سيرتي الذاتية';

  @override
  String get careerAdvice => 'نصائح مهنية';

  @override
  String get giveCareerAdvice => 'أعطني نصائح مهنية بناءً على مهاراتي';

  @override
  String get findCourses => 'البحث عن دورات';

  @override
  String get recommendCourses => 'اقترح دورات لتحسين مهاراتي';

  @override
  String get hiHowCanIHelp => 'مرحباً! كيف أستطيع مساعدتك اليوم؟';

  @override
  String get askAboutCareer => 'اسألني أي شيء عن تطورك المهني';

  @override
  String get failedToLoadCourseDetails => 'فشل في تحميل الدورة';

  @override
  String get courseNotFoundMsg => 'الدورة غير موجودة';

  @override
  String get enrolledLabel => 'مسجل';

  @override
  String get completedLabel => 'مكتمل';

  @override
  String get notEnrolledLabel => 'غير مسجل';

  @override
  String get courseProgressTitle => 'تقدم الدورة';

  @override
  String get courseDetailsTitle => 'تفاصيل الدورة';

  @override
  String get titleLabel => 'العنوان';

  @override
  String get categoryLabel => 'الفئة';

  @override
  String get platformLabel => 'المنصة';

  @override
  String get statusLabel => 'الحالة';

  @override
  String get markAsCompletedBtn => 'تحديد كمكتملة';

  @override
  String get deleteCourseBtn => 'حذف الدورة';

  @override
  String get deleteBtn => 'حذف';

  @override
  String get notStartedStatus => 'لم تبدأ';

  @override
  String get inProgressStatus => 'قيد التقدم';

  @override
  String get completedStatus => 'مكتملة';

  @override
  String areYouSureDeleteCourse(String title) {
    return 'هل أنت متأكد من حذف \"$title\"؟';
  }

  @override
  String get failedToLoadRoadmap => 'فشل في تحميل خطة التعلم';

  @override
  String get noRoadmapAvailable => 'لا توجد خطة تعلم متاحة';

  @override
  String get completeSkillsFirst => 'أكمل تحليل مهاراتك أولاً';

  @override
  String get learningRoadmap => 'خطة التعلم';

  @override
  String get personalizedPath => 'مسار التعلم المخصص لك';

  @override
  String get overallProgress => 'التقدم الكلي';

  @override
  String phasesProgress(int completed, int total) {
    return '$completed من $total مراحل';
  }

  @override
  String get learningPhases => 'مراحل التعلم';

  @override
  String duration(String value) {
    return 'المدة: $value';
  }

  @override
  String topicsCount(int count) {
    return '$count مواضيع';
  }

  @override
  String get recommendedResources => 'الموارد الموصى بها:';

  @override
  String get skillAnalysisTitle => 'تحليل المهارات';

  @override
  String get orText => 'أو';

  @override
  String get uploadResume => 'رفع السيرة الذاتية';

  @override
  String get resumeSelected => 'تم اختيار السيرة الذاتية';

  @override
  String get pdfDocDocx => 'PDF أو DOC أو DOCX';

  @override
  String get removeFile => 'إزالة الملف';

  @override
  String get orTypeSkills => 'أو اكتب مهاراتك';

  @override
  String get skillsHintText => 'مثال: JavaScript, React, TypeScript...';

  @override
  String get analyzeNow => 'تحليل الآن';

  @override
  String errorSelectingFile(String error) {
    return 'خطأ في اختيار الملف: $error';
  }

  @override
  String get pleaseUploadOrEnter =>
      'يرجى رفع سيرة ذاتية أو إدخال مهاراتك يدوياً';

  @override
  String get analysisCompletedSuccess => 'اكتمل التحليل بنجاح!';

  @override
  String get analyzingResume => 'جاري تحليل سيرتك الذاتية...';

  @override
  String get mayTakeMoments => 'قد يستغرق هذا بضع لحظات';

  @override
  String get strongSkills => 'المهارات القوية';

  @override
  String get skillsToDevelop => 'مهارات للتطوير';

  @override
  String get predictedCareer => 'المسار المهني المتوقع';

  @override
  String levelLabel(String level) {
    return '📊 المستوى: $level';
  }

  @override
  String get readyToCreatePath => 'جاهز لإنشاء مسار تعلمك؟';

  @override
  String get generatePersonalizedRoadmap =>
      'إنشاء خطة تعلم مخصصة بناءً على تحليل مهاراتك';

  @override
  String get generateLearningRoadmap => 'إنشاء خطة التعلم ←';

  @override
  String get roadmapGenerated => '🎉 تم إنشاء خطة التعلم! تحقق من تبويب التقدم';

  @override
  String get analyzingText => 'جاري التحليل...';

  @override
  String get careerDirection => 'التوجه المهني';

  @override
  String get jobOpportunities => 'فرص العمل';

  @override
  String get basedOnProfile => 'بناءً على ملفك الشخصي:';

  @override
  String get recommendationsTitle => 'التوصيات';

  @override
  String languageChangedTo(String name) {
    return 'تم تغيير اللغة إلى $name';
  }

  @override
  String failedToUpdateLanguage(String error) {
    return 'فشل في تحديث اللغة: $error';
  }

  @override
  String get selectLanguageTitle => 'اختر اللغة';

  @override
  String get languageTitle => 'اللغة';

  @override
  String get dayMon => 'إثن';

  @override
  String get dayTue => 'ثلا';

  @override
  String get dayWed => 'أرب';

  @override
  String get dayThu => 'خمي';

  @override
  String get dayFri => 'جمع';

  @override
  String get daySat => 'سبت';

  @override
  String get daySun => 'أحد';

  @override
  String get startJourneyTitle => 'ابدأ رحلتك المهنية!';

  @override
  String get startJourneyDesc =>
      'ارفع سيرتك الذاتية لاكتشاف مهاراتك والحصول على مسار تعلم مخصص.';

  @override
  String get analyzeMyCV => 'حلل سيرتي الذاتية ←';

  @override
  String get roadmapReadyTitle => 'مسار التعلم جاهز!';

  @override
  String get roadmapReadyDesc => 'اطلع على خطة التعلم المخصصة وابدأ التعلم.';

  @override
  String get viewRoadmap => 'عرض الخطة ←';

  @override
  String get newAnalysis => 'تحليل جديد';

  @override
  String roadmapStepsProgress(Object completed, Object total) {
    return '$completed/$total خطوة';
  }

  @override
  String coursesProgress(Object completed, Object total) {
    return '$completed/$total دورة';
  }

  @override
  String get analyzeFirst =>
      'حلل سيرتك الذاتية أولاً للحصول على مسار تعلم مخصص.';

  @override
  String get goToAnalysis => 'اذهب للتحليل';

  @override
  String get autoGeneratingRoadmap => 'جارٍ إنشاء مسار التعلم...';

  @override
  String get navAnalysis => 'تحليل المهارات';

  @override
  String get navRoadmap => 'الخطة';

  @override
  String get navAdvisor => 'المساعد';

  @override
  String get resumeQuality => 'جودة السيرة الذاتية';

  @override
  String get excellent => 'ممتازة';

  @override
  String get acceptable => 'مقبولة';

  @override
  String wordsCount(int count) {
    return '$count كلمة';
  }

  @override
  String get uploadingResume => 'جارٍ رفع سيرتك الذاتية...';

  @override
  String get extractingText => 'جارٍ استخراج النص...';

  @override
  String get aiSkillAnalysis => 'تحليل المهارات بالذكاء الاصطناعي...';

  @override
  String get careerMatching => 'مطابقة قاعدة البيانات المهنية...';

  @override
  String get processing => 'جارٍ المعالجة...';

  @override
  String get uploadingDesc => 'رفع سيرتك الذاتية بشكل آمن إلى الخادم';

  @override
  String get extractingDesc => 'قراءة واستخراج المحتوى من مستندك';

  @override
  String get analyzingDesc => 'نموذج الذكاء الاصطناعي يحدد مهاراتك وخبراتك';

  @override
  String get matchingDesc => 'مقارنة ملفك الشخصي مع معايير O*NET المهنية';

  @override
  String get processingDesc => 'يرجى الانتظار أثناء معالجة سيرتك الذاتية';

  @override
  String get usuallyTakes => 'عادة ما يستغرق 30-60 ثانية';

  @override
  String get uploadFile => 'رفع الملف';

  @override
  String get extractText => 'استخراج النص';

  @override
  String get createLearningPath => 'إنشاء مسار التعلم';

  @override
  String get generatingPath => 'جارٍ الإنشاء...';

  @override
  String get profilePhotoUpdated => 'تم تحديث صورة الملف الشخصي ✅';

  @override
  String get failedUploadPhoto => 'فشل في رفع الصورة';

  @override
  String get showLess => 'عرض أقل';

  @override
  String get couldNotOpenLink => 'لا يمكن فتح هذا الرابط';

  @override
  String showMoreResources(int count) {
    return 'عرض $count موارد إضافية';
  }

  @override
  String get showMore => 'عرض المزيد';

  @override
  String get reanalysisWarningTitle => 'إعادة تحليل السيرة الذاتية؟';

  @override
  String get reanalysisWarningBody =>
      'سيتم أرشفة التحليل السابق وخارطة الطريق، ومسح سجل الدردشة للتركيز على السيرة الذاتية الجديدة.';

  @override
  String get continueText => 'متابعة';

  @override
  String get languages => 'اللغات';

  @override
  String get strengths => 'نقاط القوة';

  @override
  String fileTooLarge(String size) {
    return 'الملف كبير جداً ($size ميجابايت). الحد الأقصى 10 ميجابايت.';
  }

  @override
  String get tapToSelectFile => 'اضغط لاختيار ملف';

  @override
  String get pdfDocxUpTo10 => 'PDF، DOCX — حتى 10 ميجابايت';

  @override
  String get newChat => 'محادثة جديدة';

  @override
  String get couldNotConnectAssistant => 'تعذر الاتصال بالمساعد';

  @override
  String get videos => 'فيديوهات';

  @override
  String get courses => 'دورات';

  @override
  String get phaseCompleted => 'اكتملت المرحلة!';

  @override
  String get of_ => 'من';

  @override
  String get resourcesCompleted => 'مكتمل';

  @override
  String get resourcesTotal => 'مورد';

  @override
  String get articles => 'مقالات';

  @override
  String get phases => 'مراحل';

  @override
  String get techSkills => 'الأدوات التقنية';

  @override
  String get hardSkills => 'الكفاءات الأساسية';

  @override
  String get softSkills => 'المهارات المهنية';

  @override
  String get errorArabicCV =>
      'يرجى رفع سيرة ذاتية بالإنجليزية. السير الذاتية العربية غير مدعومة حالياً.';

  @override
  String get errorInvalidCV =>
      'الملف المرفوع لا يبدو أنه سيرة ذاتية صالحة. يرجى التحقق والمحاولة مرة أخرى.';

  @override
  String get errorImagePDF =>
      'ملف PDF عبارة عن صورة (ممسوح ضوئياً). يرجى رفع ملف PDF نصي أو DOCX.';

  @override
  String get errorOldDocFormat =>
      'صيغة .doc القديمة غير مدعومة. يرجى التحويل إلى .docx أو .pdf.';

  @override
  String get errorUnsupportedFormat =>
      'صيغة الملف غير مدعومة. يرجى استخدام PDF أو DOCX.';

  @override
  String get errorQuotaExceeded =>
      'الخدمة غير متاحة مؤقتاً بسبب الضغط. يرجى المحاولة لاحقاً.';

  @override
  String get errorFileTooLarge => 'الملف كبير جداً. الحد الأقصى 10 ميجابايت.';

  @override
  String get errorConnectionTimeout =>
      'انتهت مهلة الاتصال. يرجى التحقق من اتصال الإنترنت.';

  @override
  String get errorNoConnection =>
      'تعذر الاتصال بالخادم. يرجى التحقق من اتصال الإنترنت.';

  @override
  String get errorAnalysisTimeout =>
      'استغرق التحليل وقتاً طويلاً. يرجى المحاولة مرة أخرى.';

  @override
  String get errorGeneric => 'حدث خطأ. يرجى المحاولة مرة أخرى.';

  @override
  String get phoneNumber => 'رقم الهاتف';

  @override
  String get bioHint => 'أخبرنا عن نفسك...';

  @override
  String get memberSince => 'عضو منذ';

  @override
  String get topics => 'المواضيع';

  @override
  String get yourJourney => 'رحلتك';

  @override
  String get cvAnalyzed => 'تم تحليل السيرة الذاتية';

  @override
  String get roadmapReady => 'تم إنشاء خطة التعلم';

  @override
  String get learningStarted => 'التعلم قيد التقدم';

  @override
  String get phaseNotFound => 'المرحلة غير موجودة';

  @override
  String get appDescription =>
      'تطبيق تطوير مهني وتحليل مهارات مدعوم بالذكاء الاصطناعي';

  @override
  String notifWelcomeTitle(String name) {
    return 'مرحباً بك في فيورا، $name!';
  }

  @override
  String get notifWelcomeMessage =>
      'ابدأ رحلتك المهنية برفع سيرتك الذاتية للحصول على تحليل مخصص.';

  @override
  String get notifCvAnalysisTitle => 'اكتمل تحليل السيرة الذاتية';

  @override
  String notifCvAnalysisMessage(
      String jobTitle, int skillsFound, int gapsFound) {
    return 'تم تحليل سيرتك الذاتية! الدور المتوقع: $jobTitle. تم العثور على $skillsFound مهارة وتحديد $gapsFound فجوة مهارية.';
  }

  @override
  String get notifRoadmapTitle => 'خطة التعلم جاهزة';

  @override
  String notifRoadmapMessage(int phaseCount, int totalTopics) {
    return 'خطة التعلم المخصصة جاهزة! $phaseCount مراحل تحتوي على $totalTopics موضوع لإتقانها.';
  }

  @override
  String get notifCourseCompletedTitle => 'اكتملت الدورة! 🎉';

  @override
  String notifCourseCompletedMessage(String courseTitle) {
    return 'تهانينا! لقد أكملت \'$courseTitle\'. واصل العمل الرائع!';
  }

  @override
  String get notifProfileUpdatedTitle => 'تم تحديث الملف الشخصي';

  @override
  String get notifProfileUpdatedMessage =>
      'تم تحديث معلومات ملفك الشخصي بنجاح.';

  @override
  String get notifPhaseCompletedTitle => 'اكتملت المرحلة! 🏆';

  @override
  String notifPhaseCompletedMessage(String phaseName) {
    return 'تقدم رائع! لقد أكملت مرحلة \'$phaseName\'. جاهز للتحدي التالي؟';
  }

  @override
  String showAllCount(int count) {
    return 'عرض الكل ($count)';
  }

  @override
  String get appCopyright => '© 2026 فيورا';
}
