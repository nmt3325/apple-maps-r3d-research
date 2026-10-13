
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint * huff16_decompress(uint *param_1,uint *param_2,undefined1 param_3 [8],uint *param_4,
                        uint *param_5,ulong param_6)

{
  long lVar1;
  undefined4 *puVar2;
  int *piVar3;
  undefined8 *puVar4;
  uint uVar5;
  ushort uVar6;
  undefined2 uVar7;
  uint uVar8;
  uint uVar9;
  code *pcVar10;
  bool bVar11;
  uint *puVar12;
  long lVar13;
  long lVar14;
  uint uVar15;
  uint uVar16;
  int iVar17;
  uint uVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  ulong uVar22;
  long lVar23;
  undefined1 auVar24 [8];
  uint uVar25;
  uint uVar26;
  uint uVar27;
  ulong uVar28;
  long lVar29;
  uint *unaff_x19;
  long unaff_x20;
  long lVar30;
  ulong uVar31;
  ulong unaff_x21;
  uint *puVar32;
  uint *unaff_x22;
  ulong uVar33;
  ulong uVar34;
  uint *unaff_x23;
  ulong uVar35;
  uint *unaff_x24;
  uint *puVar36;
  uint *puVar37;
  uint *puVar38;
  uint *unaff_x25;
  ulong *unaff_x26;
  ulong *unaff_x27;
  ulong uVar39;
  int iVar40;
  ulong *unaff_x28;
  ulong *puVar41;
  ulong *puVar42;
  uint uVar43;
  ulong unaff_x30;
  undefined8 uVar44;
  undefined8 uVar45;
  undefined8 uVar46;
  undefined1 auVar47 [16];
  undefined1 auStack_44a0 [8];
  undefined1 auStack_4498 [8];
  undefined1 auStack_4490 [8];
  undefined1 auStack_4488 [8];
  undefined8 uStack_4480;
  undefined8 uStack_4478;
  undefined8 uStack_4470;
  undefined8 uStack_4468;
  undefined8 uStack_4460;
  undefined8 uStack_4458;
  undefined8 uStack_4450;
  undefined8 uStack_4448;
  undefined8 uStack_4440;
  undefined8 uStack_4438;
  undefined8 uStack_4430;
  undefined8 uStack_4428;
  undefined8 uStack_4420;
  undefined8 uStack_4418;
  undefined8 uStack_4410;
  undefined8 uStack_4408;
  uint auStack_4400 [4096];
  long lStack_400;
  ulong *puStack_3f0;
  ulong *puStack_3e8;
  ulong *puStack_3e0;
  uint *puStack_3d8;
  uint *puStack_3d0;
  uint *puStack_3c8;
  uint *puStack_3c0;
  ulong uStack_3b8;
  long lStack_3b0;
  uint *puStack_3a8;
  undefined1 *puStack_3a0;
  code *pcStack_398;
  uint *puStack_388;
  uint *puStack_380;
  uint *puStack_378;
  ulong auStack_370 [64];
  uint auStack_170 [64];
  long lStack_70;
  
  lStack_70 = *_DAT_1e016af20;
  if ((long)param_2 < 4) {
LAB_1b709cc30:
    param_2 = param_5;
    puVar12 = (uint *)0xffffffffffffffff;
    puVar32 = param_4;
    goto LAB_1b709cc34;
  }
  uVar26 = *param_1;
  unaff_x19 = param_1;
  if ((uVar26 & 0x7f000000) != 0x61000000) {
    param_5 = param_2;
    if (uVar26 >> 0x18 == 0x24) {
      puVar32 = param_1;
      if ((uVar26 & 0x240000ff) == 0x24000000) {
        if ((uVar26 & 0xff00) != 0) {
          puVar41 = (ulong *)((ulong)(uVar26 >> 8) & 0xff);
          auStack_170[0] = param_1[1];
          unaff_x21 = (ulong)auStack_170[0];
          auStack_370[0] = *(ulong *)(param_1 + 2);
          puVar32 = (uint *)((long)param_1 + unaff_x21 + 0x10);
          lVar13 = (long)param_2 + (-0x10 - unaff_x21);
          uVar35 = auStack_370[0] + unaff_x21 +
                   (auStack_370[0] & ((long)auStack_370[0] >> 0x3f ^ 0xffffffffffffffffU));
          uVar35 = uVar35 & ((long)uVar35 >> 0x3f ^ 0xffffffffffffffffU);
          if ((int)puVar41 == 1) {
            puVar41 = (ulong *)0x1;
          }
          else {
            lVar23 = (long)puVar41 + -1;
            lVar14 = 1;
            uVar22 = auStack_370[0];
            do {
              uVar33 = (ulong)*puVar32;
              uVar31 = *(ulong *)(puVar32 + 1);
              auStack_170[lVar14] = *puVar32;
              auStack_370[lVar14] = uVar31;
              if ((long)uVar22 < (long)uVar31) {
                uVar22 = uVar31;
              }
              uVar22 = uVar22 + uVar31 + uVar33;
              if ((long)uVar35 <= (long)uVar22) {
                uVar35 = uVar22;
              }
              puVar32 = (uint *)((long)puVar32 + uVar33 + 0xc);
              lVar13 = (lVar13 - uVar33) + -0xc;
              lVar14 = lVar14 + 1;
              lVar23 = lVar23 + -1;
              uVar22 = uVar31;
            } while (lVar23 != 0);
          }
          puVar12 = (uint *)(lVar13 + -0xc);
          puStack_388 = param_4;
          puStack_380 = (uint *)param_3;
          unaff_x20 = func_0x0001b8120b80(uVar35,0x3065a8b);
          unaff_x22 = puVar32 + 3;
          unaff_x28 = puVar41;
          puStack_378 = puVar12;
          if ((long)puVar12 < 0) {
            unaff_x23 = puVar12;
            if (puVar41 != (ulong *)(ulong)*(byte *)((long)param_1 + 1)) {
              unaff_x24 = (uint *)auStack_370[(long)puVar41];
              while( true ) {
                if (unaff_x28 == (ulong *)0x0) {
                  unaff_x25 = (uint *)(unaff_x20 +
                                      ((ulong)unaff_x24 &
                                      ((long)unaff_x24 >> 0x3f ^ 0xffffffffffffffffU)));
                  func_0x0001b8120bb0(unaff_x25,unaff_x22,unaff_x21);
                  func_0x0001b8120bb0((long)unaff_x25 + unaff_x21,unaff_x20,unaff_x24);
                  goto LAB_1b709cfe8;
                }
                unaff_x27 = (ulong *)((long)unaff_x28 + -1);
                unaff_x23 = (uint *)auStack_370[(long)unaff_x27];
                puVar32 = unaff_x24;
                if ((long)unaff_x24 <= (long)unaff_x23) {
                  puVar32 = unaff_x23;
                }
                unaff_x25 = (uint *)(unaff_x20 + (long)puVar32);
                unaff_x26 = (ulong *)(ulong)auStack_170[(long)unaff_x28];
                func_0x0001b8120bb0(unaff_x25,unaff_x22,unaff_x26);
                param_3 = (undefined1  [8])unaff_x24;
                func_0x0001b8120bb0((long)unaff_x25 + (long)unaff_x26,unaff_x20);
                param_2 = (uint *)((long)unaff_x24 + (long)unaff_x26);
                if ((long)param_2 < 0) break;
                param_6 = 8;
                param_3 = (undefined1  [8])unaff_x23;
                param_4 = unaff_x25;
                lVar13 = FUN_1b709d024(unaff_x20,0);
                if ((lVar13 < 0) ||
                   (unaff_x22 = (uint *)((long)unaff_x22 +
                                        (-0xc - (ulong)auStack_170[(long)unaff_x27])),
                   unaff_x24 = unaff_x23, unaff_x28 = unaff_x27,
                   unaff_x27 == (ulong *)(ulong)*(byte *)((long)param_1 + 1))) break;
              }
            }
          }
          else {
            unaff_x27 = auStack_370;
            unaff_x23 = auStack_170;
            do {
              unaff_x21 = 0xfffffffffffffff4;
              if (unaff_x28 == (ulong *)(ulong)*(byte *)((long)param_1 + 1)) {
                unaff_x26 = (ulong *)((long)puVar41 + -1);
                param_3 = (undefined1  [8])unaff_x27[(long)unaff_x26];
                param_6 = 8;
                param_4 = unaff_x22;
                param_2 = puStack_378;
                lVar13 = FUN_1b709d024(unaff_x20,0);
                puVar12 = (uint *)0xffffffffffffffff;
                if ((unaff_x28 == (ulong *)0x0) || (lVar13 < 0)) goto LAB_1b709d00c;
              }
              else {
                if (unaff_x28 == (ulong *)0x0) {
                  puVar32 = (uint *)0x0;
                }
                else {
                  puVar32 = (uint *)unaff_x27[(long)puVar41 + -1];
                }
                unaff_x24 = (uint *)unaff_x27[(long)puVar41];
                puVar12 = unaff_x24;
                if ((long)unaff_x24 <= (long)puVar32) {
                  puVar12 = puVar32;
                }
                unaff_x25 = (uint *)(unaff_x20 + (long)puVar12);
                unaff_x21 = (ulong)unaff_x23[(long)puVar41];
                func_0x0001b8120bb0(unaff_x25,unaff_x22,unaff_x21);
                param_3 = (undefined1  [8])unaff_x24;
                func_0x0001b8120bb0((long)unaff_x25 + unaff_x21,unaff_x20);
                unaff_x26 = puVar41;
                if (unaff_x28 == (ulong *)0x0) goto LAB_1b709cfe8;
                param_2 = (uint *)((long)unaff_x24 + unaff_x21);
                if ((long)param_2 < 0) break;
                unaff_x26 = (ulong *)((long)puVar41 + -1);
                param_3 = (undefined1  [8])unaff_x27[(long)unaff_x26];
                param_6 = 8;
                param_4 = unaff_x25;
                lVar13 = FUN_1b709d024(unaff_x20,0);
                unaff_x21 = 0xfffffffffffffff4;
                if (lVar13 < 0) break;
              }
              puVar41 = (ulong *)((long)puVar41 + -1);
              unaff_x21 = 0xfffffffffffffff4;
              unaff_x22 = (uint *)((long)unaff_x22 + (-0xc - (ulong)unaff_x23[(long)puVar41]));
              puVar42 = (ulong *)((long)unaff_x28 + -1);
              bVar11 = 0 < (long)unaff_x28;
              unaff_x26 = puVar41;
              unaff_x28 = puVar42;
            } while (bVar11);
          }
          goto LAB_1b709d008;
        }
        bVar11 = param_2 < (uint *)0x10;
        param_2 = param_2 + -4;
        param_5 = param_2;
        if (bVar11) goto LAB_1b709cc30;
        puVar32 = param_1 + 4;
      }
      param_6 = 0x10;
      puVar12 = (uint *)FUN_1b709d024(0,param_3);
      param_3 = (undefined1  [8])param_4;
      goto LAB_1b709cc34;
    }
    goto LAB_1b709cc30;
  }
  if (*_DAT_1e016af20 == lStack_70) {
    if (((unaff_x30 ^ unaff_x30 << 1) >> 0x3e & 1) != 0) {
                    /* WARNING: Does not return */
      pcVar10 = (code *)SoftwareBreakpoint(0xc471,0x1b709cce0);
      (*pcVar10)();
    }
    puVar32 = (uint *)FUN_1b709d024(0,param_3,param_4,param_1,param_2,0x10);
    return puVar32;
  }
  goto LAB_1b709d020;
code_r0x0001b709d484:
  uVar39 = uVar39 + 1;
  uVar28 = uVar28 - 1;
  if (uVar33 == uVar39) goto LAB_1b709d444;
  goto LAB_1b709d474;
  while( true ) {
    uVar15 = uVar15 + 1;
    uVar43 = uVar43 - 1;
    if (uVar43 == 0) break;
LAB_1b709dc70:
    uVar27 = 0;
    if (uVar25 != 0) {
      uVar27 = uVar15 / uVar25;
    }
    uVar15 = uVar15 - uVar27 * uVar25;
    if (*(int *)(lVar14 + (ulong)uVar15 * 8 + 4) == 0) {
      auStack_4490._0_4_ = auStack_4490._0_4_ + 1;
      puVar37 = (uint *)(lVar14 + (ulong)uVar15 * 8);
      *puVar37 = uVar18;
      puVar37[1] = uVar9;
      break;
    }
  }
LAB_1b709dcb0:
  lVar23 = lVar30 + (long)iVar17 * 8;
  *(undefined2 *)(lVar13 + (long)puVar12 * 2) = *(undefined2 *)(lVar23 + 6);
  uVar6 = *(ushort *)(lVar23 + 4);
  uVar22 = (ulong)uVar6;
  if (iVar19 < (int)(uint)uVar6) {
    if ((long)uVar35 < 4) {
      uVar31 = 0;
      puVar37 = puVar38;
    }
    else {
      puVar37 = puVar38 + 1;
      uVar31 = (ulong)*puVar38;
    }
    puVar32 = (uint *)(uVar31 << ((ulong)(0x20 - iVar19) & 0x3f) | (ulong)puVar32);
LAB_1b709dac0:
    uVar35 = uVar35 - 4;
    iVar19 = iVar19 + 0x20;
    puVar38 = puVar37;
  }
LAB_1b709dac4:
  iVar19 = iVar19 - (int)uVar22;
  puVar32 = (uint *)((long)puVar32 << (uVar22 & 0x3f));
  puVar12 = (uint *)((long)puVar12 + 1);
  uVar22 = uVar35;
  puVar37 = puVar38;
  if ((undefined1  [8])puVar12 == auStack_4498) goto LAB_1b709ddf4;
  goto LAB_1b709dad8;
  while( true ) {
    uVar15 = uVar15 + 1;
    uVar43 = uVar43 - 1;
    if (uVar43 == 0) break;
LAB_1b709d958:
    uVar27 = 0;
    if (uVar25 != 0) {
      uVar27 = uVar15 / uVar25;
    }
    uVar15 = uVar15 - uVar27 * uVar25;
    if (*(int *)(lVar13 + (ulong)uVar15 * 8 + 4) == 0) {
      auStack_4490._0_4_ = auStack_4490._0_4_ + 1;
      puVar38 = (uint *)(lVar13 + (ulong)uVar15 * 8);
      *puVar38 = uVar18;
      puVar38[1] = uVar9;
      break;
    }
  }
LAB_1b709d7b0:
  lVar23 = lVar30 + (long)iVar17 * 8;
  *(undefined1 *)(lVar14 + (long)puVar12) = *(undefined1 *)(lVar23 + 6);
  uVar6 = *(ushort *)(lVar23 + 4);
LAB_1b709d7c0:
  iVar19 = iVar19 - (uint)uVar6;
  puVar32 = (uint *)((long)puVar32 << ((ulong)uVar6 & 0x3f));
  puVar12 = (uint *)((long)puVar12 + 1);
  uVar22 = uVar35;
  if ((undefined1  [8])puVar12 == auStack_4498) goto LAB_1b709ddf4;
  goto LAB_1b709d7d4;
LAB_1b709cfe8:
  param_2 = (uint *)(unaff_x21 + (long)unaff_x24);
  param_3 = (undefined1  [8])puStack_388;
  if ((long)param_2 < 0) {
LAB_1b709d008:
    puVar12 = (uint *)0xffffffffffffffff;
  }
  else {
    param_6 = 0x10;
    param_4 = unaff_x25;
    puVar12 = (uint *)FUN_1b709d024(0,puStack_380);
  }
LAB_1b709d00c:
  func_0x0001b81206e0(unaff_x20);
  puVar32 = param_4;
  unaff_x19 = puVar12;
LAB_1b709cc34:
  param_1 = puVar12;
  param_4 = puVar32;
  if (*_DAT_1e016af20 == lStack_70) {
    return puVar12;
  }
LAB_1b709d020:
  func_0x0001b811fac0(param_1);
  pcStack_398 = FUN_1b709d024;
  puStack_3f0 = unaff_x28;
  puStack_3e8 = unaff_x27;
  puStack_3e0 = unaff_x26;
  puStack_3d8 = unaff_x25;
  puStack_3d0 = unaff_x24;
  puStack_3c8 = unaff_x23;
  puStack_3c0 = unaff_x22;
  uStack_3b8 = unaff_x21;
  lStack_3b0 = unaff_x20;
  puStack_3a8 = unaff_x19;
  puStack_3a0 = &stack0xfffffffffffffff0;
  auVar47 = (*_DAT_1e8d38a30)();
  lVar13 = auVar47._8_8_;
  lVar14 = auVar47._0_8_;
  lStack_400 = *_DAT_1e016af20;
  uStack_4418 = 0;
  uStack_4420 = 0;
  uStack_4408 = 0;
  uStack_4410 = 0;
  iVar17 = (int)param_6;
  uStack_4438 = 0;
  uStack_4440 = 0;
  uStack_4428 = 0;
  uStack_4430 = 0;
  iVar19 = 0xc;
  if (iVar17 == 8) {
    iVar19 = 0xd;
  }
  uStack_4458 = 0;
  uStack_4460 = 0;
  uStack_4448 = 0;
  uStack_4450 = 0;
  uStack_4478 = 0;
  uStack_4480 = 0;
  uStack_4468 = 0;
  uStack_4470 = 0;
  puVar32 = (uint *)param_3;
  if (param_2 == (uint *)0x0) {
joined_r0x0001b709d0e4:
    if (puVar32 == (uint *)0x0) goto LAB_1b709d0ec;
  }
  else {
    puVar32 = param_2 + -1;
    if ((uint *)0x3 < param_2) {
      puVar12 = param_4 + 1;
      uVar25 = *param_4;
      uVar26 = uVar25 & 0x800000ff;
      bVar11 = (uVar25 & 0x7f000000) != 0x61000000;
      if (bVar11) {
        uVar26 = 0xffffffff;
      }
      if ((!bVar11 && (int)uVar26 < 3) && (uVar26 & 0x7ffffffe) != 0) {
        if ((param_3 == (undefined1  [8])0x0) || (puVar32 == (uint *)0x0)) {
          if (param_3 == (undefined1  [8])puVar32) goto LAB_1b709d0ec;
        }
        else if ((int)uVar25 < 0) {
          lVar23 = (long)param_3 << (lVar14 == 0);
          if (param_2 == (uint *)(lVar23 + 4)) {
            if (lVar14 != 0) {
              lVar13 = lVar14;
            }
            func_0x0001b8120bb0(lVar13,puVar12,lVar23);
            goto LAB_1b709d0ec;
          }
        }
        else {
          if (puVar32 < (uint *)0x4) {
            lVar30 = 0;
          }
          else {
            auStack_44a0 = (undefined1  [8])
                           (((ulong)param_4[1] << 0x20) >> ((ulong)(uint)-iVar17 & 0x3f));
            puVar38 = param_4 + 2;
            param_2 = param_2 + -2;
            auStack_4488 = (undefined1  [8])(param_6 & 0xffffffff);
            auStack_4490 = (undefined1  [8])(ulong)(0x40 - iVar17);
            uVar22 = ((ulong)param_4[1] << 0x20) << (param_6 & 0x3f);
            uVar26 = SUB84(auStack_44a0,0) + 1;
            uVar31 = (ulong)uVar26;
            uVar39 = uVar22 >> 0x3d;
            iVar21 = 0x1d - iVar17;
            uVar33 = uVar22 << 3;
            auStack_4498 = param_3;
            lVar30 = func_0x0001b8120b80(uVar31 << 3,0x100004000313f17);
            auVar24 = auStack_44a0;
            iVar20 = 0;
            lVar23 = 0;
            uVar25 = (uint)(param_6 >> 1) & 0x7fffffff;
            uVar35 = uVar31;
            do {
              if (uVar39 == 0) {
                puVar37 = (uint *)(lVar30 + lVar23 * 8);
                puVar36 = param_2;
                if (uVar26 == 2) {
                  *(undefined2 *)(puVar37 + 1) = 1;
                  if (iVar21 < 1) {
                    puVar36 = param_2 + -1;
                    if ((long)param_2 < 4) {
                      uVar28 = 0;
                    }
                    else {
                      uVar28 = (ulong)*puVar38;
                      puVar38 = puVar38 + 1;
                    }
                    uVar33 = uVar28 << ((ulong)(0x20 - iVar21) & 0x3f) | uVar33;
                    iVar21 = iVar21 + 0x20;
                  }
                  iVar40 = iVar21 + -1;
                  uVar34 = uVar33 << 1;
                  *puVar37 = (uint)(uVar33 >> 0x3f);
                }
                else {
                  *puVar37 = 0;
                  *(undefined2 *)(puVar37 + 1) = 0;
                  uVar34 = uVar33;
                  iVar40 = iVar21;
                }
              }
              else {
                uVar5 = (uint)(uVar22 >> 0x20);
                puVar37 = param_2;
                if (iVar21 < (int)(uVar5 >> 0x1d)) {
                  puVar37 = param_2 + -1;
                  if ((long)param_2 < 4) {
                    uVar28 = 0;
                  }
                  else {
                    uVar28 = (ulong)*puVar38;
                    puVar38 = puVar38 + 1;
                  }
                  uVar33 = uVar28 << ((ulong)(0x20 - iVar21) & 0x3f) | uVar33;
                  iVar21 = iVar21 + 0x20;
                }
                iVar21 = iVar21 - (uVar5 >> 0x1d);
                uVar28 = uVar33 << uVar39;
                uVar5 = (int)(uVar33 >> (0x40 - uVar39 & 0x3f)) + 1;
                puVar2 = (undefined4 *)(lVar30 + lVar23 * 8);
                *(short *)(puVar2 + 1) = (short)uVar5;
                uVar5 = uVar5 & 0xffff;
                puVar36 = puVar37;
                if (iVar21 < (int)uVar5) {
                  puVar36 = puVar37 + -1;
                  if ((long)puVar37 < 4) {
                    uVar33 = 0;
                  }
                  else {
                    uVar33 = (ulong)*puVar38;
                    puVar38 = puVar38 + 1;
                  }
                  uVar28 = uVar33 << ((ulong)(0x20 - iVar21) & 0x3f) | uVar28;
                  iVar21 = iVar21 + 0x20;
                }
                iVar40 = iVar21 - uVar5;
                uVar34 = uVar28 << ((ulong)uVar5 & 0x3f);
                *puVar2 = (int)(uVar28 >> ((ulong)-uVar5 & 0x3f));
              }
              param_2 = puVar36;
              if (iVar40 < 1) {
                param_2 = puVar36 + -1;
                if ((long)puVar36 < 4) {
                  uVar33 = 0;
                }
                else {
                  uVar33 = (ulong)*puVar38;
                  puVar38 = puVar38 + 1;
                }
                uVar34 = uVar33 << ((ulong)(0x20 - iVar40) & 0x3f) | uVar34;
                iVar40 = iVar40 + 0x20;
              }
              iVar21 = iVar40 + -1;
              uVar33 = uVar34 << 1;
              if ((long)uVar34 < 0) {
                puVar37 = param_2;
                if (iVar40 < 2) {
                  puVar37 = param_2 + -1;
                  if ((long)param_2 < 4) {
                    uVar28 = 0;
                  }
                  else {
                    uVar28 = (ulong)*puVar38;
                    puVar38 = puVar38 + 1;
                  }
                  uVar33 = uVar28 << ((ulong)(0x21 - iVar40) & 0x3f) | uVar33;
                  iVar21 = iVar40 + 0x1f;
                }
                iVar40 = iVar21 + -1;
                uVar28 = uVar33 << 1;
                param_2 = puVar37;
                if ((long)uVar33 < 0) {
                  if (iVar21 <= iVar17) {
                    param_2 = puVar37 + -1;
                    if ((long)puVar37 < 4) {
                      uVar33 = 0;
                    }
                    else {
                      uVar33 = (ulong)*puVar38;
                      puVar38 = puVar38 + 1;
                    }
                    uVar28 = uVar33 << ((ulong)(0x21 - iVar21) & 0x3f) | uVar28;
                    iVar40 = iVar21 + 0x1f;
                  }
                  iVar20 = (int)(uVar28 >> ((ulong)auStack_4490 & 0x3f));
                  iVar21 = iVar40 - iVar17;
                  uVar33 = uVar28 << ((ulong)auStack_4488 & 0x3f);
                }
                else {
                  puVar36 = puVar38;
                  if (iVar21 <= (int)uVar25) {
                    param_2 = puVar37 + -1;
                    if ((long)puVar37 < 4) {
                      uVar33 = 0;
                    }
                    else {
                      puVar36 = puVar38 + 1;
                      uVar33 = (ulong)*puVar38;
                    }
                    uVar28 = uVar33 << ((ulong)(0x21 - iVar21) & 0x3f) | uVar28;
                    iVar40 = iVar21 + 0x1f;
                  }
                  iVar21 = iVar40 - uVar25;
                  uVar33 = uVar28 << (param_6 >> 1 & 0x3f);
                  iVar20 = iVar20 + (int)(uVar28 >> ((ulong)(0x40 - uVar25) & 0x3f));
                  puVar38 = puVar36;
                }
              }
              *(short *)(lVar30 + lVar23 * 8 + 6) = (short)iVar20;
              iVar20 = iVar20 + 1;
              lVar23 = lVar23 + 1;
              uVar35 = uVar35 - 1;
            } while (uVar35 != 0);
            if (-1 < (long)param_2) {
              puVar37 = (uint *)((long)puVar12 + ((long)puVar38 - (long)puVar12));
              uVar35 = (long)puVar32 - ((long)puVar38 - (long)puVar12);
              if (-1 < (long)uVar35) {
                uVar22 = 0;
                uVar33 = 0;
                do {
                  iVar20 = (int)uVar33;
                  if (0 < iVar20) {
                    uVar39 = 0;
                    uVar6 = *(ushort *)(lVar30 + uVar22 * 8 + 4);
                    uVar26 = (uint)uVar6;
                    uVar28 = uVar33;
LAB_1b709d474:
                    uVar25 = *(uint *)((long)&uStack_4480 + uVar39 * 4);
                    if (uVar25 != uVar6) {
                      if ((int)uVar25 < (int)(uint)uVar6) goto code_r0x0001b709d484;
                      uVar25 = (uint)uVar39;
                      if (iVar20 <= (int)uVar25) goto LAB_1b709d520;
                      uVar34 = uVar33 - uVar39;
                      if (uVar34 < 8) goto LAB_1b709d504;
                      lVar23 = 0;
                      uVar28 = uVar28 & 0xfffffffffffffff8;
                      do {
                        lVar29 = (uVar33 - lVar23) * 4;
                        uVar44 = *(undefined8 *)(auStack_4490 + lVar29);
                        uVar46 = *(undefined8 *)(auStack_4498 + lVar29);
                        uVar45 = *(undefined8 *)(auStack_44a0 + lVar29);
                        lVar1 = (uVar33 - lVar23) * 4;
                        *(undefined8 *)(auStack_4488 + lVar1 + 4) =
                             *(undefined8 *)(auStack_4488 + lVar29);
                        *(undefined8 *)(auStack_4490 + lVar1 + 4) = uVar44;
                        *(undefined8 *)(auStack_4498 + lVar1 + 4) = uVar46;
                        *(undefined8 *)(auStack_44a0 + lVar1 + 4) = uVar45;
                        lVar23 = lVar23 + 8;
                        uVar28 = uVar28 - 8;
                      } while (uVar28 != 0);
                      if (uVar34 != (uVar34 & 0xfffffffffffffff8)) {
                        uVar33 = uVar33 - (uVar34 & 0xfffffffffffffff8);
LAB_1b709d504:
                        do {
                          uVar28 = uVar33 - 1;
                          *(undefined4 *)((long)&uStack_4480 + uVar33 * 4) =
                               *(undefined4 *)((long)&uStack_4480 + uVar28 * 4);
                          uVar33 = uVar28;
                        } while ((long)(int)uVar25 < (long)uVar28);
                      }
LAB_1b709d520:
                      *(uint *)((long)&uStack_4480 + uVar39 * 4) = uVar26;
                      uVar33 = (ulong)(iVar20 + 1U);
                      if (uVar25 == iVar20 + 1U) goto LAB_1b709d530;
                      goto LAB_1b709d44c;
                    }
                    goto LAB_1b709d49c;
                  }
                  uVar39 = 0;
LAB_1b709d49c:
                  if ((int)uVar39 == iVar20) {
LAB_1b709d530:
                    iVar20 = (int)uVar39;
                    uVar26 = (uint)*(ushort *)(lVar30 + uVar22 * 8 + 4);
LAB_1b709d444:
                    uVar33 = (ulong)(iVar20 + 1);
                    *(uint *)((long)&uStack_4480 + (long)iVar20 * 4) = uVar26;
                  }
LAB_1b709d44c:
                  bVar11 = (undefined1  [8])uVar22 != auVar24;
                  uVar22 = uVar22 + 1;
                } while (bVar11);
                iVar21 = (int)uVar33;
                uVar22 = (long)iVar21 - 1;
                iVar20 = *(int *)((long)&uStack_4480 + uVar22 * 4);
                if (iVar21 < 1) {
                  uVar26 = 0;
                  iVar40 = 0;
                  if (iVar21 != 0) {
                    iVar40 = iVar19;
                  }
                }
                else {
                  do {
                    iVar40 = *(int *)((long)&uStack_4480 + (uVar22 & 0xffffffff) * 4);
                    if (iVar40 <= iVar19) goto LAB_1b709d570;
                    uVar26 = (int)uVar22 - 1;
                    uVar22 = (ulong)uVar26;
                  } while (uVar26 != 0xffffffff);
                  iVar40 = 0;
LAB_1b709d570:
                  lVar23 = 0;
                  uVar26 = 0;
                  do {
                    iVar19 = *(int *)((long)&uStack_4480 + lVar23 * 4);
                    if (iVar40 < iVar19) {
                      *(int *)((long)&uStack_4480 + (long)(int)uVar26 * 4) = iVar19;
                      uVar26 = uVar26 + 1;
                    }
                    lVar23 = lVar23 + 1;
                    uVar33 = uVar33 - 1;
                  } while (uVar33 != 0);
                }
                if (iVar17 == 8) {
                  func_0x0001b811fc60(auStack_4400,0x4000);
                  if (auVar24 == (undefined1  [8])0x0) {
                    if (0 < (long)auStack_4498) {
                      func_0x0001b8120bd0(lVar14,*(undefined1 *)(lVar30 + 6),auStack_4498);
                    }
                    goto LAB_1b709de84;
                  }
                  if (iVar40 < iVar20) {
                    uVar25 = 0x3fd;
                    lVar13 = func_0x0001b8120b70(0x3fd,8,0x100004000313f17);
                  }
                  else {
                    lVar13 = 0;
                    uVar25 = 0;
                  }
                  uVar22 = 0;
                  iVar19 = 0;
                  uVar5 = uVar25;
                  if (uVar25 < 2) {
                    uVar5 = 1;
                  }
                  do {
                    piVar3 = (int *)(lVar30 + uVar22 * 8);
                    uVar6 = *(ushort *)(piVar3 + 1);
                    uVar43 = iVar40 - (uint)uVar6;
                    if (iVar40 < (int)(uint)uVar6) {
                      uVar15 = *piVar3 << (ulong)(iVar20 - (uint)uVar6 & 0x1f);
                      uVar43 = (uVar15 ^ uVar15 >> 0x10) * -0x7a143595;
                      uVar43 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                      uVar43 = uVar43 ^ uVar43 >> 0x10;
                      uVar27 = uVar5;
                      do {
                        uVar18 = 0;
                        if (uVar25 != 0) {
                          uVar18 = uVar43 / uVar25;
                        }
                        uVar43 = uVar43 - uVar18 * uVar25;
                        if (*(int *)(lVar13 + (ulong)uVar43 * 8 + 4) == 0) {
                          iVar19 = iVar19 + 1;
                          puVar32 = (uint *)(lVar13 + (ulong)uVar43 * 8);
                          *puVar32 = uVar15;
                          puVar32[1] = (int)uVar22 + 1;
                          break;
                        }
                        uVar43 = uVar43 + 1;
                        uVar27 = uVar27 - 1;
                      } while (uVar27 != 0);
                    }
                    else {
                      uVar27 = *piVar3 << (ulong)(uVar43 & 0x1f);
                      uVar6 = *(ushort *)((long)piVar3 + 6) | uVar6 << 8;
                      *(ushort *)((long)auStack_4400 + (ulong)uVar27 * 2) = uVar6;
                      uVar15 = 1;
                      do {
                        *(ushort *)((long)auStack_4400 + (ulong)((uVar27 + uVar15) - 1) * 2) = uVar6
                        ;
                        uVar18 = uVar15 >> (ulong)(uVar43 & 0x1f);
                        uVar15 = uVar15 + 1;
                      } while (uVar18 == 0);
                    }
                    uVar22 = uVar22 + 1;
                  } while (uVar22 != uVar31);
                  if (iVar40 < iVar20) {
                    if (0 < (long)auStack_4498) {
                      auStack_4490._0_4_ = iVar19;
                      iVar19 = 0;
                      puVar32 = (uint *)0x0;
                      puVar12 = (uint *)0x0;
                      uVar22 = uVar35;
LAB_1b709d7d4:
                      if (iVar40 < 1) {
LAB_1b709d824:
                        uVar35 = uVar22;
                        if (iVar19 < iVar20) {
                          uVar35 = uVar22 - 4;
                          if ((long)uVar22 < 4) {
                            uVar22 = 0;
                          }
                          else {
                            uVar22 = (ulong)*puVar37;
                            puVar37 = puVar37 + 1;
                          }
                          puVar32 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                            (ulong)puVar32);
                          iVar19 = iVar19 + 0x20;
                        }
                        uVar18 = (uint)((ulong)puVar32 >> ((ulong)(0x40 - iVar20) & 0x3f));
                        uVar43 = (uVar18 ^ uVar18 >> 0x10) * -0x7a143595;
                        uVar15 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                        uVar15 = uVar15 ^ uVar15 >> 0x10;
                        uVar27 = uVar5;
                        uVar43 = uVar15;
                        do {
                          uVar8 = 0;
                          if (uVar25 != 0) {
                            uVar8 = uVar43 / uVar25;
                          }
                          uVar43 = uVar43 - uVar8 * uVar25;
                          puVar38 = (uint *)(lVar13 + (ulong)uVar43 * 8);
                          uVar8 = puVar38[1];
                          if (*puVar38 == uVar18) {
                            iVar17 = uVar8 - 1;
                            goto LAB_1b709d8a4;
                          }
                          if (uVar8 == 0) break;
                          uVar43 = uVar43 + 1;
                          uVar27 = uVar27 - 1;
                        } while (uVar27 != 0);
                        iVar17 = -1;
LAB_1b709d8a4:
                        if ((0 < (int)uVar26) && (iVar17 == -1)) {
                          auStack_4488 = (undefined1  [8])uVar35;
                          uVar22 = 0;
                          do {
                            uVar8 = *(uint *)((long)&uStack_4480 + uVar22 * 4);
                            uVar27 = -1 << (ulong)(iVar20 - uVar8 & 0x1f) & uVar18;
                            uVar43 = (uVar27 ^ uVar27 >> 0x10) * -0x7a143595;
                            uVar43 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                            uVar43 = uVar43 ^ uVar43 >> 0x10;
                            uVar16 = uVar25;
                            do {
                              uVar9 = 0;
                              if (uVar25 != 0) {
                                uVar9 = uVar43 / uVar25;
                              }
                              uVar43 = uVar43 - uVar9 * uVar25;
                              puVar38 = (uint *)(lVar13 + (ulong)uVar43 * 8);
                              uVar9 = puVar38[1];
                              if (*puVar38 == uVar27) {
                                if ((uVar9 != 0) &&
                                   (iVar17 = uVar9 - 1,
                                   uVar8 == *(ushort *)(lVar30 + (long)iVar17 * 8 + 4))) {
                                  uVar43 = uVar25;
                                  if (uVar25 <= (uint)(auStack_4490._0_4_ * 2)) goto LAB_1b709d7b0;
                                  goto LAB_1b709d958;
                                }
                                break;
                              }
                              if (uVar9 == 0) break;
                              uVar43 = uVar43 + 1;
                              uVar16 = uVar16 - 1;
                            } while (uVar16 != 0);
                            uVar22 = uVar22 + 1;
                          } while (uVar22 != uVar26);
                          iVar17 = -1;
                        }
                        goto LAB_1b709d7b0;
                      }
                      uVar35 = uVar22;
                      if (iVar19 < iVar40) {
                        uVar35 = uVar22 - 4;
                        if ((long)uVar22 < 4) {
                          uVar22 = 0;
                        }
                        else {
                          uVar22 = (ulong)*puVar37;
                          puVar37 = puVar37 + 1;
                        }
                        puVar32 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                          (ulong)puVar32);
                        iVar19 = iVar19 + 0x20;
                      }
                      uVar6 = *(ushort *)
                               ((long)auStack_4400 +
                               ((ulong)puVar32 >> ((ulong)(0x40 - iVar40) & 0x3f)) * 2);
                      uVar22 = uVar35;
                      if (uVar6 == 0) goto LAB_1b709d824;
                      *(char *)(lVar14 + (long)puVar12) = (char)uVar6;
                      uVar6 = uVar6 >> 8;
                      goto LAB_1b709d7c0;
                    }
LAB_1b709ddf0:
                    puVar32 = (uint *)0x0;
LAB_1b709ddf4:
                    func_0x0001b81206e0();
                  }
                  else {
                    if ((long)auStack_4498 < 1) goto LAB_1b709de84;
                    puVar32 = (uint *)0x0;
                    iVar19 = 0;
                    lVar13 = 0;
                    auVar24 = auStack_4498;
                    uVar22 = uVar35;
                    do {
                      uVar35 = uVar22;
                      puVar12 = puVar37;
                      if (iVar19 < iVar40) {
                        uVar35 = uVar22 - 4;
                        if ((long)uVar22 < 4) {
                          uVar22 = 0;
                        }
                        else {
                          puVar12 = puVar37 + 1;
                          uVar22 = (ulong)*puVar37;
                        }
                        puVar32 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                          (ulong)puVar32);
                        iVar19 = iVar19 + 0x20;
                      }
                      uVar6 = *(ushort *)
                               ((long)auStack_4400 +
                               ((ulong)puVar32 >> ((ulong)(0x40 - iVar40) & 0x3f)) * 2);
                      *(char *)(lVar14 + lVar13) = (char)uVar6;
                      uVar6 = uVar6 >> 8;
                      iVar19 = iVar19 - (uint)uVar6;
                      puVar32 = (uint *)((long)puVar32 << ((ulong)uVar6 & 0x3f));
                      lVar13 = lVar13 + 1;
                      auVar24 = (undefined1  [8])((long)auVar24 + -1);
                      uVar22 = uVar35;
                      puVar37 = puVar12;
                    } while (auVar24 != (undefined1  [8])0x0);
                  }
                }
                else {
                  func_0x0001b811fc60(auStack_4400,0x4000);
                  if (auVar24 == (undefined1  [8])0x0) {
                    if (0 < (long)auStack_4498) {
                      uVar7 = *(undefined2 *)(lVar30 + 6);
                      if ((ulong)auStack_4498 < (uint *)0x4) {
                        puVar32 = (uint *)0x0;
                      }
                      else {
                        if ((ulong)auStack_4498 < (uint *)0x10) {
                          puVar12 = (uint *)0x0;
                        }
                        else {
                          lVar14 = 0;
                          puVar32 = (uint *)((ulong)auStack_4498 & 0x7ffffffffffffff0);
                          uVar44 = CONCAT26(uVar7,CONCAT24(uVar7,CONCAT22(uVar7,uVar7)));
                          uVar45 = CONCAT26(uVar7,CONCAT24(uVar7,CONCAT22(uVar7,uVar7)));
                          puVar12 = puVar32;
                          do {
                            puVar4 = (undefined8 *)(lVar13 + lVar14 * 2);
                            puVar4[1] = uVar45;
                            *puVar4 = uVar44;
                            puVar4[3] = uVar45;
                            puVar4[2] = uVar44;
                            lVar14 = lVar14 + 0x10;
                            puVar12 = puVar12 + -4;
                          } while (puVar12 != (uint *)0x0);
                          if (auStack_4498 == (undefined1  [8])puVar32) goto LAB_1b709de84;
                          puVar12 = puVar32;
                          if (((ulong)auStack_4498 & 0xc) == 0) goto LAB_1b709de70;
                        }
                        puVar32 = (uint *)((ulong)auStack_4498 & 0x7ffffffffffffffc);
                        lVar14 = (long)puVar12 - (long)puVar32;
                        do {
                          *(ulong *)(lVar13 + (long)puVar12 * 2) =
                               CONCAT26(uVar7,CONCAT24(uVar7,CONCAT22(uVar7,uVar7)));
                          puVar12 = puVar12 + 1;
                          lVar14 = lVar14 + 4;
                        } while (lVar14 != 0);
                        if (auStack_4498 == (undefined1  [8])puVar32) goto LAB_1b709de84;
                      }
LAB_1b709de70:
                      lVar14 = (long)auStack_4498 - (long)puVar32;
                      do {
                        *(undefined2 *)(lVar13 + (long)puVar32 * 2) = uVar7;
                        puVar32 = (uint *)((long)puVar32 + 1);
                        lVar14 = lVar14 + -1;
                      } while (lVar14 != 0);
                    }
                  }
                  else {
                    if (iVar40 < iVar20) {
                      uVar25 = 0x1ffff;
                      lVar14 = func_0x0001b8120b70(0x1ffff,8,0x100004000313f17);
                    }
                    else {
                      lVar14 = 0;
                      uVar25 = 0;
                    }
                    uVar22 = 0;
                    iVar19 = 0;
                    uVar5 = uVar25;
                    if (uVar25 < 2) {
                      uVar5 = 1;
                    }
                    do {
                      piVar3 = (int *)(lVar30 + uVar22 * 8);
                      uVar6 = *(ushort *)(piVar3 + 1);
                      uVar43 = iVar40 - (uint)uVar6;
                      if (iVar40 < (int)(uint)uVar6) {
                        uVar15 = *piVar3 << (ulong)(iVar20 - (uint)uVar6 & 0x1f);
                        uVar43 = (uVar15 ^ uVar15 >> 0x10) * -0x7a143595;
                        uVar43 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                        uVar43 = uVar43 ^ uVar43 >> 0x10;
                        uVar27 = uVar5;
                        do {
                          uVar18 = 0;
                          if (uVar25 != 0) {
                            uVar18 = uVar43 / uVar25;
                          }
                          uVar43 = uVar43 - uVar18 * uVar25;
                          if (*(int *)(lVar14 + (ulong)uVar43 * 8 + 4) == 0) {
                            iVar19 = iVar19 + 1;
                            puVar32 = (uint *)(lVar14 + (ulong)uVar43 * 8);
                            *puVar32 = uVar15;
                            puVar32[1] = (int)uVar22 + 1;
                            break;
                          }
                          uVar43 = uVar43 + 1;
                          uVar27 = uVar27 - 1;
                        } while (uVar27 != 0);
                      }
                      else {
                        uVar27 = *piVar3 << (ulong)(uVar43 & 0x1f);
                        uVar18 = CONCAT22(uVar6,*(undefined2 *)((long)piVar3 + 6));
                        auStack_4400[uVar27] = uVar18;
                        uVar15 = 1;
                        do {
                          auStack_4400[(uVar27 + uVar15) - 1] = uVar18;
                          uVar8 = uVar15 >> (ulong)(uVar43 & 0x1f);
                          uVar15 = uVar15 + 1;
                        } while (uVar8 == 0);
                      }
                      uVar22 = uVar22 + 1;
                    } while (uVar22 != uVar31);
                    if (iVar40 < iVar20) {
                      if (0 < (long)auStack_4498) {
                        auStack_4490._0_4_ = iVar19;
                        iVar19 = 0;
                        puVar32 = (uint *)0x0;
                        puVar12 = (uint *)0x0;
                        uVar22 = uVar35;
LAB_1b709dad8:
                        puVar38 = puVar37;
                        if (iVar40 < 1) {
LAB_1b709db3c:
                          uVar35 = uVar22;
                          if (iVar19 < iVar20) {
                            uVar35 = uVar22 - 4;
                            if ((long)uVar22 < 4) {
                              uVar22 = 0;
                            }
                            else {
                              uVar22 = (ulong)*puVar38;
                              puVar38 = puVar38 + 1;
                            }
                            puVar32 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                              (ulong)puVar32);
                            iVar19 = iVar19 + 0x20;
                          }
                          uVar18 = (uint)((ulong)puVar32 >> ((ulong)(0x40 - iVar20) & 0x3f));
                          uVar43 = (uVar18 ^ uVar18 >> 0x10) * -0x7a143595;
                          uVar15 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                          uVar15 = uVar15 ^ uVar15 >> 0x10;
                          uVar27 = uVar5;
                          uVar43 = uVar15;
                          do {
                            uVar8 = 0;
                            if (uVar25 != 0) {
                              uVar8 = uVar43 / uVar25;
                            }
                            uVar43 = uVar43 - uVar8 * uVar25;
                            puVar37 = (uint *)(lVar14 + (ulong)uVar43 * 8);
                            uVar8 = puVar37[1];
                            if (*puVar37 == uVar18) {
                              iVar17 = uVar8 - 1;
                              goto LAB_1b709dbbc;
                            }
                            if (uVar8 == 0) break;
                            uVar43 = uVar43 + 1;
                            uVar27 = uVar27 - 1;
                          } while (uVar27 != 0);
                          iVar17 = -1;
LAB_1b709dbbc:
                          if ((0 < (int)uVar26) && (iVar17 == -1)) {
                            auStack_4488 = (undefined1  [8])uVar35;
                            uVar22 = 0;
                            do {
                              uVar8 = *(uint *)((long)&uStack_4480 + uVar22 * 4);
                              uVar27 = -1 << (ulong)(iVar20 - uVar8 & 0x1f) & uVar18;
                              uVar43 = (uVar27 ^ uVar27 >> 0x10) * -0x7a143595;
                              uVar43 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                              uVar43 = uVar43 ^ uVar43 >> 0x10;
                              uVar16 = uVar25;
                              do {
                                uVar9 = 0;
                                if (uVar25 != 0) {
                                  uVar9 = uVar43 / uVar25;
                                }
                                uVar43 = uVar43 - uVar9 * uVar25;
                                puVar37 = (uint *)(lVar14 + (ulong)uVar43 * 8);
                                uVar9 = puVar37[1];
                                if (*puVar37 == uVar27) {
                                  if ((uVar9 != 0) &&
                                     (iVar17 = uVar9 - 1,
                                     uVar8 == *(ushort *)(lVar30 + (long)iVar17 * 8 + 4))) {
                                    uVar43 = uVar25;
                                    if (uVar25 <= (uint)(auStack_4490._0_4_ * 2))
                                    goto LAB_1b709dcb0;
                                    goto LAB_1b709dc70;
                                  }
                                  break;
                                }
                                if (uVar9 == 0) break;
                                uVar43 = uVar43 + 1;
                                uVar16 = uVar16 - 1;
                              } while (uVar16 != 0);
                              uVar22 = uVar22 + 1;
                            } while (uVar22 != uVar26);
                            iVar17 = -1;
                          }
                          goto LAB_1b709dcb0;
                        }
                        uVar35 = uVar22;
                        if (iVar19 < iVar40) {
                          uVar35 = uVar22 - 4;
                          if ((long)uVar22 < 4) {
                            uVar22 = 0;
                          }
                          else {
                            uVar22 = (ulong)*puVar37;
                            puVar37 = puVar37 + 1;
                          }
                          puVar32 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                            (ulong)puVar32);
                          iVar19 = iVar19 + 0x20;
                        }
                        uVar43 = auStack_4400[(ulong)puVar32 >> ((ulong)(0x40 - iVar40) & 0x3f)];
                        uVar22 = uVar35;
                        puVar38 = puVar37;
                        if (uVar43 == 0) goto LAB_1b709db3c;
                        *(short *)(lVar13 + (long)puVar12 * 2) = (short)uVar43;
                        uVar22 = (ulong)(uVar43 >> 0x10);
                        if (iVar19 < (int)(uVar43 >> 0x10)) {
                          if ((long)uVar35 < 4) {
                            uVar31 = 0;
                          }
                          else {
                            uVar31 = (ulong)*puVar37;
                            puVar37 = puVar37 + 1;
                          }
                          puVar32 = (uint *)(uVar31 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                            (ulong)puVar32);
                          goto LAB_1b709dac0;
                        }
                        goto LAB_1b709dac4;
                      }
                      goto LAB_1b709ddf0;
                    }
                    if (0 < (long)auStack_4498) {
                      puVar32 = (uint *)0x0;
                      iVar19 = 0;
                      lVar14 = 0;
                      auVar24 = auStack_4498;
                      uVar22 = uVar35;
                      do {
                        uVar35 = uVar22;
                        puVar12 = puVar37;
                        if (iVar19 < iVar40) {
                          uVar35 = uVar22 - 4;
                          if ((long)uVar22 < 4) {
                            uVar22 = 0;
                          }
                          else {
                            puVar12 = puVar37 + 1;
                            uVar22 = (ulong)*puVar37;
                          }
                          puVar32 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                            (ulong)puVar32);
                          iVar19 = iVar19 + 0x20;
                        }
                        uVar26 = auStack_4400[(ulong)puVar32 >> ((ulong)(0x40 - iVar40) & 0x3f)];
                        *(short *)(lVar13 + lVar14 * 2) = (short)uVar26;
                        uVar26 = uVar26 >> 0x10;
                        iVar19 = iVar19 - uVar26;
                        puVar32 = (uint *)((long)puVar32 << ((ulong)uVar26 & 0x3f));
                        lVar14 = lVar14 + 1;
                        auVar24 = (undefined1  [8])((long)auVar24 + -1);
                        uVar22 = uVar35;
                        puVar37 = puVar12;
                      } while (auVar24 != (undefined1  [8])0x0);
                      goto LAB_1b709de88;
                    }
                  }
LAB_1b709de84:
                  puVar32 = (uint *)0x0;
                }
LAB_1b709de88:
                if (0xfffffffffffffffa < uVar35 - 1) {
                  if (uVar35 != 0xfffffffffffffffc) {
                    func_0x0001b81206e0(lVar30);
                    param_3 = auStack_4498;
                    goto LAB_1b709d0ec;
                  }
                  func_0x0001b81206e0(lVar30);
                  param_3 = auStack_4498;
                  goto joined_r0x0001b709d0e4;
                }
              }
            }
          }
          func_0x0001b81206e0(lVar30);
        }
      }
    }
  }
  param_3 = (undefined1  [8])(uint *)0xffffffffffffffff;
LAB_1b709d0ec:
  if (*_DAT_1e016af20 == lStack_400) {
    return (uint *)param_3;
  }
  func_0x0001b811fac0();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

