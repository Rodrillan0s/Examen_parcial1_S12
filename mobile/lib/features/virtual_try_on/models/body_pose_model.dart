import 'dart:math' as math;

class BodyPoint {
  final double x;
  final double y;
  final double confidence;

  const BodyPoint({
    required this.x,
    required this.y,
    required this.confidence,
  });

  double distanceTo(BodyPoint other) {
    final dx = x - other.x;
    final dy = y - other.y;
    return math.sqrt(dx * dx + dy * dy);
  }

  static BodyPoint midpoint(BodyPoint a, BodyPoint b) {
    return BodyPoint(
      x: (a.x + b.x) / 2,
      y: (a.y + b.y) / 2,
      confidence: math.min(a.confidence, b.confidence),
    );
  }
}

class BodyPose {
  final BodyPoint? nose;
  final BodyPoint? leftShoulder;
  final BodyPoint? rightShoulder;
  final BodyPoint? leftElbow;
  final BodyPoint? rightElbow;
  final BodyPoint? leftWrist;
  final BodyPoint? rightWrist;
  final BodyPoint? leftHip;
  final BodyPoint? rightHip;
  final BodyPoint? leftKnee;
  final BodyPoint? rightKnee;
  final BodyPoint? leftAnkle;
  final BodyPoint? rightAnkle;

  const BodyPose({
    this.nose,
    this.leftShoulder,
    this.rightShoulder,
    this.leftElbow,
    this.rightElbow,
    this.leftWrist,
    this.rightWrist,
    this.leftHip,
    this.rightHip,
    this.leftKnee,
    this.rightKnee,
    this.leftAnkle,
    this.rightAnkle,
  });

  bool get hasShoulders =>
      leftShoulder != null &&
      rightShoulder != null &&
      leftShoulder!.confidence >= 0.45 &&
      rightShoulder!.confidence >= 0.45;

  bool get hasHips =>
      leftHip != null &&
      rightHip != null &&
      leftHip!.confidence >= 0.45 &&
      rightHip!.confidence >= 0.45;

  bool get hasKnees =>
      leftKnee != null &&
      rightKnee != null &&
      leftKnee!.confidence >= 0.45 &&
      rightKnee!.confidence >= 0.45;

  bool get hasLeftArm =>
      leftShoulder != null &&
      leftElbow != null &&
      leftShoulder!.confidence >= 0.35 &&
      leftElbow!.confidence >= 0.35;

  bool get hasRightArm =>
      rightShoulder != null &&
      rightElbow != null &&
      rightShoulder!.confidence >= 0.35 &&
      rightElbow!.confidence >= 0.35;

  bool get hasArms => hasLeftArm || hasRightArm;

  bool get hasFullArms => hasLeftArm && hasRightArm;

  bool get hasForearms =>
      (leftElbow != null && leftWrist != null && leftElbow!.confidence >= 0.35 && leftWrist!.confidence >= 0.35) ||
      (rightElbow != null && rightWrist != null && rightElbow!.confidence >= 0.35 && rightWrist!.confidence >= 0.35);

  bool get isBodyDetected => hasShoulders || hasHips;
}

