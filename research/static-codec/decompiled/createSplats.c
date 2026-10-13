
undefined8 createSplats(ulong *param_1,ulong *param_2)

{
  undefined8 *puVar1;
  int *piVar2;
  undefined8 *puVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  undefined1 auVar10 [16];
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];
  undefined8 uVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  int iVar19;
  uint uVar20;
  code *pcVar21;
  bool bVar22;
  bool bVar23;
  uint uVar24;
  long lVar25;
  long lVar26;
  ulong uVar27;
  int iVar28;
  long lVar29;
  ulong uVar30;
  int iVar31;
  undefined8 uVar32;
  undefined8 *puVar33;
  bool bVar34;
  uint uVar35;
  uint uVar36;
  uint uVar37;
  uint uVar38;
  uint uVar39;
  ulong uVar40;
  ulong uVar41;
  undefined8 uVar42;
  undefined8 uVar43;
  float fVar44;
  undefined4 uVar45;
  undefined4 uVar46;
  ulong uVar47;
  undefined8 uVar48;
  float fVar49;
  float fVar50;
  undefined4 uVar51;
  undefined1 auVar52 [16];
  undefined1 auVar53 [16];
  undefined8 uVar54;
  undefined8 uVar55;
  undefined8 uVar56;
  undefined8 uVar57;
  float unaff_s8;
  ulong uVar58;
  undefined8 uStack_f0;
  undefined8 uStack_e8;
  ulong uStack_b8;
  ulong uStack_b0;
  ulong uStack_a8;
  ulong uStack_a0;
  ulong uStack_98;
  ulong uStack_90;
  ulong uStack_88;
  ulong uStack_80;
  ulong uStack_78;
  
  uVar27 = param_1[1];
  if ((int)uVar27 == 0) {
    return 1;
  }
  uVar40 = param_1[0x79];
  fVar44 = *(float *)(param_1 + 0x7a);
  fVar50 = (float)(uVar40 >> 0x20);
  fVar49 = (float)uVar40 * (float)uVar40;
  fVar50 = fVar50 * fVar50;
  auVar52._4_4_ = fVar50;
  auVar52._0_4_ = fVar49;
  auVar52._8_4_ = fVar44 * fVar44;
  auVar52._12_4_ = 0;
  auVar10._4_4_ = fVar50;
  auVar10._0_4_ = fVar49;
  auVar10._8_4_ = fVar44 * fVar44;
  auVar10._12_4_ = 0;
  auVar52 = NEON_ext(auVar52,auVar10,8,1);
  fVar49 = fVar49 + auVar52._0_4_ + fVar50 + auVar52._4_4_;
  if (fVar49 <= 0.0) {
    uVar40 = param_1[0x4a];
    fVar44 = *(float *)(param_1 + 0x4b);
    fVar50 = (float)(uVar40 >> 0x20);
    fVar49 = (float)uVar40 * (float)uVar40;
    fVar50 = fVar50 * fVar50;
    auVar11._4_4_ = fVar50;
    auVar11._0_4_ = fVar49;
    auVar11._8_4_ = fVar44 * fVar44;
    auVar11._12_4_ = 0;
    auVar12._4_4_ = fVar50;
    auVar12._0_4_ = fVar49;
    auVar12._8_4_ = fVar44 * fVar44;
    auVar12._12_4_ = 0;
    auVar52 = NEON_ext(auVar11,auVar12,8,1);
    fVar49 = fVar49 + auVar52._0_4_ + fVar50 + auVar52._4_4_;
    if (0.0 < fVar49) {
      lVar25 = 0x264;
      lVar26 = 0x260;
      lVar29 = 0x25c;
      goto LAB_1b70ae94c;
    }
    uVar45 = 0;
    bVar34 = false;
    uStack_e8 = 0;
    uStack_f0 = 0;
  }
  else {
    lVar25 = 0x3dc;
    lVar26 = 0x3d8;
    lVar29 = 0x3d4;
LAB_1b70ae94c:
    fVar49 = 1.0 / SQRT(fVar49);
    unaff_s8 = fVar49 * fVar44;
    uVar45 = *(undefined4 *)((long)param_1 + lVar29);
    uStack_f0 = CONCAT44(*(undefined4 *)((long)param_1 + lVar25),
                         *(undefined4 *)((long)param_1 + lVar26));
    uStack_e8 = CONCAT44(fVar49 * (float)(uVar40 >> 0x20),fVar49 * (float)uVar40);
    bVar34 = true;
  }
  uStack_b8 = param_1[9];
  uVar47 = param_1[10];
  uStack_88 = param_1[0xb];
  uStack_b0 = param_1[0xc];
  uStack_98 = param_1[0xd];
  uStack_80 = param_1[0xe];
  uStack_a8 = param_1[0xf];
  uVar46 = (undefined4)uStack_a8;
  uVar51 = (undefined4)(uStack_a8 >> 0x20);
  auVar53._0_8_ = param_1[0x10];
  auVar53._8_8_ = 0;
  uStack_78 = param_1[0x11];
  uVar30 = param_1[0x13];
  uVar40 = param_1[0x12];
  uVar58 = param_1[0x14];
  uStack_a0 = uVar47;
  uStack_90 = auVar53._0_8_;
  uVar41 = func_0x0001b6679b38(&uStack_b8);
  param_2[4] = uVar47;
  param_2[5] = CONCAT44(uVar51,uVar46);
  param_2[6] = auVar53._0_8_;
  param_2[1] = uVar30;
  *param_2 = uVar40;
  param_2[2] = uVar58;
  param_2[3] = uVar41;
  func_0x0001b6224c54(param_2 + 7,(long)(int)uVar27 * 3);
  uVar27 = param_2[7];
  lVar25 = param_2[8] - uVar27;
  if (lVar25 != 0) {
    uVar41 = (lVar25 >> 2) * -0x5555555555555555;
    uVar40 = *param_1;
    if ((uVar41 < 8) || ((uVar27 < uVar40 + lVar25 && (uVar40 < param_2[8])))) {
      uVar30 = 0;
    }
    else {
      uVar47 = 0;
      uVar30 = uVar41 & 0xfffffffffffffff8;
      uVar58 = uVar30;
      do {
        puVar33 = (undefined8 *)(uVar40 + uVar47 * 0xc);
        puVar1 = (undefined8 *)(uVar40 + (uVar47 | 4) * 0xc);
        uVar43 = puVar33[1];
        uVar42 = *puVar33;
        uVar48 = puVar33[2];
        uVar13 = puVar33[5];
        uVar32 = puVar33[4];
        uVar14 = *puVar1;
        uVar15 = puVar1[1];
        uVar55 = puVar1[3];
        uVar54 = puVar1[2];
        uVar57 = puVar1[5];
        uVar56 = puVar1[4];
        puVar1 = (undefined8 *)(uVar27 + uVar47 * 0xc);
        puVar3 = (undefined8 *)(uVar27 + (uVar47 | 4) * 0xc);
        puVar1[3] = puVar33[3];
        puVar1[2] = uVar48;
        puVar1[5] = uVar13;
        puVar1[4] = uVar32;
        puVar1[1] = uVar43;
        *puVar1 = uVar42;
        puVar3[3] = uVar55;
        puVar3[2] = uVar54;
        puVar3[5] = uVar57;
        puVar3[4] = uVar56;
        puVar3[1] = uVar15;
        *puVar3 = uVar14;
        uVar47 = uVar47 + 8;
        uVar58 = uVar58 - 8;
      } while (uVar58 != 0);
      if (uVar41 - uVar30 == 0) goto LAB_1b70aea64;
    }
    lVar25 = uVar41 - uVar30;
    do {
      puVar33 = (undefined8 *)(uVar40 + uVar30 * 0xc);
      puVar1 = (undefined8 *)(uVar27 + uVar30 * 0xc);
      uVar32 = *puVar33;
      *(undefined4 *)(puVar1 + 1) = *(undefined4 *)(puVar33 + 1);
      *puVar1 = uVar32;
      uVar30 = uVar30 + 1;
      lVar25 = lVar25 + -1;
    } while (lVar25 != 0);
  }
LAB_1b70aea64:
  uVar27 = param_1[4];
  if ((long)uVar27 < 1) {
    bVar22 = false;
    bVar23 = false;
    uVar24 = 0;
    uVar40 = 0xffffffff;
    uVar35 = 0xffffffff;
    uVar37 = 0xffffffff;
    uVar36 = 0xffffffff;
    uVar39 = 0xffffffff;
  }
  else {
    lVar25 = 0;
    uVar24 = 0;
    iVar28 = 0;
    iVar31 = 0;
    uVar39 = 0xffffffff;
    uVar36 = 0xffffffff;
    uVar37 = 0xffffffff;
    uVar35 = 0xffffffff;
    uVar40 = 0xffffffff;
    do {
      piVar2 = (int *)(param_1[5] + lVar25 * 0xc);
      iVar8 = *piVar2;
      iVar9 = piVar2[2] * piVar2[1];
      uVar4 = uVar24;
      if (iVar8 != 7) {
        uVar4 = uVar35;
      }
      iVar6 = iVar9;
      uVar38 = uVar24;
      uVar16 = uVar35;
      if (iVar8 != 6) {
        iVar6 = iVar28;
        uVar38 = uVar37;
        uVar16 = uVar4;
      }
      iVar5 = iVar28;
      uVar4 = uVar24;
      uVar17 = uVar37;
      uVar18 = uVar35;
      if (iVar8 != 4) {
        iVar5 = iVar6;
        uVar4 = uVar36;
        uVar17 = uVar38;
        uVar18 = uVar16;
      }
      uVar38 = (uint)uVar40;
      iVar6 = iVar9;
      uVar16 = uVar24;
      if (iVar8 != 2) {
        iVar6 = iVar31;
        uVar16 = uVar38;
      }
      uVar7 = uVar24;
      iVar19 = iVar31;
      uVar20 = uVar38;
      if (iVar8 != 1) {
        uVar7 = uVar39;
        iVar19 = iVar6;
        uVar20 = uVar16;
      }
      if (iVar8 < 4) {
        uVar38 = uVar20;
      }
      uVar40 = (ulong)uVar38;
      if (iVar8 < 4) {
        uVar39 = uVar7;
        iVar5 = iVar28;
        iVar31 = iVar19;
        uVar4 = uVar36;
        uVar17 = uVar37;
        uVar18 = uVar35;
      }
      uVar35 = uVar18;
      uVar37 = uVar17;
      uVar36 = uVar4;
      iVar28 = iVar5;
      uVar24 = iVar9 + uVar24;
      lVar25 = lVar25 + 1;
      uVar27 = uVar27 - 1;
    } while (uVar27 != 0);
    bVar22 = iVar31 == 3;
    bVar23 = iVar28 == 2;
  }
  if (((int)param_1[3] < (int)uVar24) || (!(bool)((uVar39 | (uint)uVar40) < 0x80000000 & bVar22))) {
    return 0;
  }
  func_0x0001b6ae62ec(param_2 + 10,(long)(int)param_1[1]);
  uVar27 = param_2[10];
  if (param_2[0xb] != uVar27) {
    lVar25 = 0;
    uVar41 = 0;
    do {
      lVar26 = param_1[2] + uVar41 * (long)(int)param_1[3] * 4;
      puVar33 = (undefined8 *)(param_1[2] + uVar40 * 4 + lVar25 * (int)param_1[3]);
      uVar32 = *puVar33;
      *(uint *)(uVar27 + uVar41 * 0x14) =
           CONCAT13((char)(int)(*(float *)(lVar26 + (ulong)uVar39 * 4) * 255.0),
                    CONCAT12((char)(int)(*(float *)(puVar33 + 1) * 255.0),
                             CONCAT11((char)(int)((float)((ulong)uVar32 >> 0x20) * 255.0),
                                      (char)(int)((float)uVar32 * 255.0))));
      uVar27 = param_2[10];
      uVar30 = param_2[0xb];
      if (-1 < (int)uVar35) {
        if ((ulong)(((long)(uVar30 - uVar27) >> 2) * -0x3333333333333333) <= uVar41)
        goto LAB_1b70aec90;
        *(undefined4 *)(uVar27 + uVar41 * 0x14 + 4) = *(undefined4 *)(lVar26 + (ulong)uVar35 * 4);
      }
      uVar30 = ((long)(uVar30 - uVar27) >> 2) * -0x3333333333333333;
      if ((bool)(uVar37 < 0x80000000 & bVar23)) {
        if (uVar30 <= uVar41) goto LAB_1b70aec90;
        uVar46 = *(undefined4 *)(lVar26 + (ulong)(uVar37 + 1) * 4);
        lVar29 = uVar27 + uVar41 * 0x14;
        *(undefined4 *)(lVar29 + 8) = *(undefined4 *)(lVar26 + (ulong)uVar37 * 4);
        *(undefined4 *)(lVar29 + 0xc) = uVar46;
      }
      if (-1 < (int)uVar36) {
        if (uVar30 <= uVar41) {
LAB_1b70aec90:
                    /* WARNING: Does not return */
          pcVar21 = (code *)SoftwareBreakpoint(1,0x1b70aec94);
          (*pcVar21)();
        }
        *(undefined4 *)(uVar27 + uVar41 * 0x14 + 0x10) = *(undefined4 *)(lVar26 + (ulong)uVar36 * 4)
        ;
      }
      uVar41 = uVar41 + 1;
      lVar25 = lVar25 + 4;
    } while (uVar41 < uVar30);
  }
  if (bVar34) {
    *(float *)((long)param_2 + 0x84) = unaff_s8;
    *(undefined4 *)(param_2 + 0xe) = uVar45;
    *(undefined8 *)((long)param_2 + 0x7c) = uStack_e8;
    *(undefined8 *)((long)param_2 + 0x74) = uStack_f0;
    param_2[0xd] = param_1[8];
    return 1;
  }
  uVar32 = func_0x0001b70d8b94();
  return uVar32;
}

