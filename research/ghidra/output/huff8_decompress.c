
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Removing unreachable block (ram,0x0001b709ccdc) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint * FUN_1b709c7b4(uint *param_1,uint *param_2,undefined1 param_3 [8],uint *param_4,uint *param_5,
                    ulong param_6)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined8 *puVar3;
  uint uVar4;
  ushort uVar5;
  undefined2 uVar6;
  uint uVar7;
  uint uVar8;
  code *pcVar9;
  bool bVar10;
  uint *puVar11;
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
  uint *puVar27;
  uint uVar28;
  ulong uVar29;
  long lVar30;
  uint *unaff_x19;
  long unaff_x20;
  long lVar31;
  ulong uVar32;
  ulong unaff_x21;
  uint *unaff_x22;
  ulong uVar33;
  ulong uVar34;
  uint *unaff_x23;
  uint *puVar35;
  ulong uVar36;
  uint *unaff_x24;
  uint *unaff_x25;
  ulong *unaff_x26;
  long lVar37;
  long lVar38;
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
  undefined1 auVar48 [16];
  undefined1 auStack_4830 [8];
  undefined1 auStack_4828 [8];
  undefined1 auStack_4820 [8];
  undefined1 auStack_4818 [8];
  undefined8 uStack_4810;
  undefined8 uStack_4808;
  undefined8 uStack_4800;
  undefined8 uStack_47f8;
  undefined8 uStack_47f0;
  undefined8 uStack_47e8;
  undefined8 uStack_47e0;
  undefined8 uStack_47d8;
  undefined8 uStack_47d0;
  undefined8 uStack_47c8;
  undefined8 uStack_47c0;
  undefined8 uStack_47b8;
  undefined8 uStack_47b0;
  undefined8 uStack_47a8;
  undefined8 uStack_47a0;
  undefined8 uStack_4798;
  uint auStack_4790 [4096];
  long lStack_790;
  ulong *puStack_780;
  ulong *puStack_778;
  ulong *puStack_770;
  uint *puStack_768;
  uint *puStack_760;
  uint *puStack_758;
  uint *puStack_750;
  ulong uStack_748;
  long lStack_740;
  undefined8 uStack_738;
  undefined1 **ppuStack_730;
  code *pcStack_728;
  uint *local_718;
  uint *puStack_710;
  uint *local_708;
  ulong local_700 [64];
  uint local_500 [64];
  long local_400;
  ulong *local_3f0;
  ulong *puStack_3e8;
  ulong *local_3e0;
  uint *puStack_3d8;
  uint *local_3d0;
  uint *puStack_3c8;
  uint *local_3c0;
  ulong uStack_3b8;
  long local_3b0;
  uint *puStack_3a8;
  undefined1 *local_3a0;
  code *pcStack_398;
  uint *local_388;
  uint *puStack_380;
  uint *local_378;
  ulong local_370 [64];
  uint local_170 [64];
  long local_70;
  
  local_70 = *_DAT_1e016af20;
  if (param_2 == (uint *)0x0) {
    puVar11 = (uint *)-(ulong)(param_4 != (uint *)0x0);
    goto LAB_1b709c808;
  }
  if ((long)param_2 < 4) {
LAB_1b709c7f8:
    puVar11 = (uint *)0xffffffffffffffff;
    param_5 = param_2;
    goto LAB_1b709c808;
  }
  uVar26 = *param_1;
  unaff_x19 = param_1;
  if ((uVar26 & 0x7f000000) != 0x61000000) {
    if (uVar26 >> 0x18 == 0x24) {
      param_5 = param_2;
      if ((uVar26 & 0x240000ff) == 0x24000000) {
        if ((uVar26 & 0xff00) != 0) {
          puVar41 = (ulong *)((ulong)(uVar26 >> 8) & 0xff);
          local_170[0] = param_1[1];
          unaff_x21 = (ulong)local_170[0];
          local_370[0] = *(ulong *)(param_1 + 2);
          puVar11 = (uint *)((long)param_1 + unaff_x21 + 0x10);
          lVar13 = (long)param_2 + (-0x10 - unaff_x21);
          uVar36 = local_370[0] + unaff_x21 +
                   (local_370[0] & ((long)local_370[0] >> 0x3f ^ 0xffffffffffffffffU));
          uVar36 = uVar36 & ((long)uVar36 >> 0x3f ^ 0xffffffffffffffffU);
          if ((int)puVar41 == 1) {
            puVar41 = (ulong *)0x1;
          }
          else {
            lVar23 = (long)puVar41 + -1;
            lVar14 = 1;
            uVar22 = local_370[0];
            do {
              uVar33 = (ulong)*puVar11;
              uVar32 = *(ulong *)(puVar11 + 1);
              local_170[lVar14] = *puVar11;
              local_370[lVar14] = uVar32;
              if ((long)uVar22 < (long)uVar32) {
                uVar22 = uVar32;
              }
              uVar22 = uVar22 + uVar32 + uVar33;
              if ((long)uVar36 <= (long)uVar22) {
                uVar36 = uVar22;
              }
              puVar11 = (uint *)((long)puVar11 + uVar33 + 0xc);
              lVar13 = (lVar13 - uVar33) + -0xc;
              lVar14 = lVar14 + 1;
              lVar23 = lVar23 + -1;
              uVar22 = uVar32;
            } while (lVar23 != 0);
          }
          unaff_x23 = (uint *)(lVar13 + -0xc);
          local_388 = param_4;
          puStack_380 = (uint *)param_3;
          unaff_x20 = func_0x0001b8120b80(uVar36,0xaa625972);
          unaff_x22 = puVar11 + 3;
          local_378 = unaff_x23;
          unaff_x28 = puVar41;
          if ((long)unaff_x23 < 0) {
            if (puVar41 != (ulong *)(ulong)*(byte *)((long)param_1 + 1)) {
              unaff_x24 = (uint *)local_370[(long)puVar41];
              while( true ) {
                if (unaff_x28 == (ulong *)0x0) {
                  unaff_x25 = (uint *)(unaff_x20 +
                                      ((ulong)unaff_x24 &
                                      ((long)unaff_x24 >> 0x3f ^ 0xffffffffffffffffU)));
                  func_0x0001b8120bb0(unaff_x25,unaff_x22,unaff_x21);
                  func_0x0001b8120bb0((long)unaff_x25 + unaff_x21,unaff_x20,unaff_x24);
                  goto LAB_1b709cbb8;
                }
                unaff_x27 = (ulong *)((long)unaff_x28 + -1);
                unaff_x23 = (uint *)local_370[(long)unaff_x27];
                puVar11 = unaff_x24;
                if ((long)unaff_x24 <= (long)unaff_x23) {
                  puVar11 = unaff_x23;
                }
                unaff_x25 = (uint *)(unaff_x20 + (long)puVar11);
                unaff_x26 = (ulong *)(ulong)local_170[(long)unaff_x28];
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
                                        (-0xc - (ulong)local_170[(long)unaff_x27])),
                   unaff_x24 = unaff_x23, unaff_x28 = unaff_x27,
                   unaff_x27 == (ulong *)(ulong)*(byte *)((long)param_1 + 1))) break;
              }
            }
          }
          else {
            unaff_x27 = local_370;
            unaff_x23 = local_170;
            do {
              unaff_x21 = 0xfffffffffffffff4;
              if (unaff_x28 == (ulong *)(ulong)*(byte *)((long)param_1 + 1)) {
                unaff_x26 = (ulong *)((long)puVar41 + -1);
                param_3 = (undefined1  [8])unaff_x27[(long)unaff_x26];
                param_6 = 8;
                param_4 = unaff_x22;
                param_2 = local_378;
                lVar13 = FUN_1b709d024(unaff_x20,0);
                puVar11 = (uint *)0xffffffffffffffff;
                if ((unaff_x28 == (ulong *)0x0) || (lVar13 < 0)) goto LAB_1b709cbdc;
              }
              else {
                if (unaff_x28 == (ulong *)0x0) {
                  puVar11 = (uint *)0x0;
                }
                else {
                  puVar11 = (uint *)unaff_x27[(long)puVar41 + -1];
                }
                unaff_x24 = (uint *)unaff_x27[(long)puVar41];
                puVar27 = unaff_x24;
                if ((long)unaff_x24 <= (long)puVar11) {
                  puVar27 = puVar11;
                }
                unaff_x25 = (uint *)(unaff_x20 + (long)puVar27);
                unaff_x21 = (ulong)unaff_x23[(long)puVar41];
                func_0x0001b8120bb0(unaff_x25,unaff_x22,unaff_x21);
                param_3 = (undefined1  [8])unaff_x24;
                func_0x0001b8120bb0((long)unaff_x25 + unaff_x21,unaff_x20);
                unaff_x26 = puVar41;
                if (unaff_x28 == (ulong *)0x0) goto LAB_1b709cbb8;
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
              bVar10 = 0 < (long)unaff_x28;
              unaff_x26 = puVar41;
              unaff_x28 = puVar42;
            } while (bVar10);
          }
          goto LAB_1b709cbd8;
        }
        bVar10 = param_2 < (uint *)0x10;
        param_2 = param_2 + -4;
        if (bVar10) goto LAB_1b709c7f8;
        param_1 = param_1 + 4;
        param_5 = param_2;
      }
      param_6 = 8;
      puVar11 = (uint *)FUN_1b709d024(param_3,0);
      param_3 = (undefined1  [8])param_4;
      param_4 = param_1;
      goto LAB_1b709c808;
    }
    goto LAB_1b709c7f8;
  }
  if (*_DAT_1e016af20 == local_70) {
    if (((unaff_x30 ^ unaff_x30 << 1) >> 0x3e & 1) == 0) {
      puVar11 = (uint *)FUN_1b709d024(param_3,0,param_4,param_1,param_2,8);
      return puVar11;
    }
                    /* WARNING: Does not return */
    pcVar9 = (code *)SoftwareBreakpoint(0xc471,0x1b709c8b0);
    (*pcVar9)();
  }
  goto LAB_1b709cbf0;
LAB_1b709cfe8:
  puVar11 = (uint *)(uVar22 + (long)unaff_x24);
  param_3 = (undefined1  [8])local_718;
  if ((long)puVar11 < 0) goto LAB_1b709d008;
  param_6 = 0x10;
  param_4 = unaff_x25;
  puVar12 = (uint *)FUN_1b709d024(0,puStack_710);
  goto LAB_1b709d00c;
code_r0x0001b709d484:
  uVar39 = uVar39 + 1;
  uVar29 = uVar29 - 1;
  if (uVar33 == uVar39) goto LAB_1b709d444;
  goto LAB_1b709d474;
  while( true ) {
    uVar15 = uVar15 + 1;
    uVar43 = uVar43 - 1;
    if (uVar43 == 0) break;
LAB_1b709dc70:
    uVar28 = 0;
    if (uVar25 != 0) {
      uVar28 = uVar15 / uVar25;
    }
    uVar15 = uVar15 - uVar28 * uVar25;
    if (*(int *)(lVar14 + (ulong)uVar15 * 8 + 4) == 0) {
      auStack_4820._0_4_ = auStack_4820._0_4_ + 1;
      puVar35 = (uint *)(lVar14 + (ulong)uVar15 * 8);
      *puVar35 = uVar18;
      puVar35[1] = uVar8;
      break;
    }
  }
LAB_1b709dcb0:
  lVar23 = lVar31 + (long)iVar17 * 8;
  *(undefined2 *)(lVar13 + (long)puVar27 * 2) = *(undefined2 *)(lVar23 + 6);
  uVar5 = *(ushort *)(lVar23 + 4);
  uVar22 = (ulong)uVar5;
  if (iVar19 < (int)(uint)uVar5) {
    if ((long)uVar36 < 4) {
      uVar32 = 0;
      puVar35 = puVar12;
    }
    else {
      puVar35 = puVar12 + 1;
      uVar32 = (ulong)*puVar12;
    }
    puVar11 = (uint *)(uVar32 << ((ulong)(0x20 - iVar19) & 0x3f) | (ulong)puVar11);
LAB_1b709dac0:
    uVar36 = uVar36 - 4;
    iVar19 = iVar19 + 0x20;
    puVar12 = puVar35;
  }
LAB_1b709dac4:
  iVar19 = iVar19 - (int)uVar22;
  puVar11 = (uint *)((long)puVar11 << (uVar22 & 0x3f));
  puVar27 = (uint *)((long)puVar27 + 1);
  uVar22 = uVar36;
  puVar35 = puVar12;
  if ((undefined1  [8])puVar27 == auStack_4828) goto LAB_1b709ddf4;
  goto LAB_1b709dad8;
  while( true ) {
    uVar15 = uVar15 + 1;
    uVar43 = uVar43 - 1;
    if (uVar43 == 0) break;
LAB_1b709d958:
    uVar28 = 0;
    if (uVar25 != 0) {
      uVar28 = uVar15 / uVar25;
    }
    uVar15 = uVar15 - uVar28 * uVar25;
    if (*(int *)(lVar13 + (ulong)uVar15 * 8 + 4) == 0) {
      auStack_4820._0_4_ = auStack_4820._0_4_ + 1;
      puVar12 = (uint *)(lVar13 + (ulong)uVar15 * 8);
      *puVar12 = uVar18;
      puVar12[1] = uVar8;
      break;
    }
  }
LAB_1b709d7b0:
  lVar23 = lVar31 + (long)iVar17 * 8;
  *(undefined1 *)(lVar14 + (long)puVar27) = *(undefined1 *)(lVar23 + 6);
  uVar5 = *(ushort *)(lVar23 + 4);
LAB_1b709d7c0:
  iVar19 = iVar19 - (uint)uVar5;
  puVar11 = (uint *)((long)puVar11 << ((ulong)uVar5 & 0x3f));
  puVar27 = (uint *)((long)puVar27 + 1);
  uVar22 = uVar36;
  if ((undefined1  [8])puVar27 == auStack_4828) goto LAB_1b709ddf4;
  goto LAB_1b709d7d4;
LAB_1b709cbb8:
  param_2 = (uint *)(unaff_x21 + (long)unaff_x24);
  param_3 = (undefined1  [8])local_388;
  if ((long)param_2 < 0) {
LAB_1b709cbd8:
    puVar11 = (uint *)0xffffffffffffffff;
  }
  else {
    param_6 = 8;
    param_4 = unaff_x25;
    puVar11 = (uint *)FUN_1b709d024(puStack_380,0);
  }
LAB_1b709cbdc:
  func_0x0001b81206e0(unaff_x20);
  param_5 = param_2;
  unaff_x19 = puVar11;
LAB_1b709c808:
  param_1 = puVar11;
  param_2 = param_5;
  if (*_DAT_1e016af20 == local_70) {
    return puVar11;
  }
LAB_1b709cbf0:
  auVar47 = func_0x0001b811fac0(param_1);
  auVar48._8_8_ = param_2;
  auVar48._0_8_ = unaff_x19;
  puVar11 = auVar47._8_8_;
  puVar27 = auVar47._0_8_;
  pcStack_398 = huff16_decompress;
  local_400 = *_DAT_1e016af20;
  local_3f0 = unaff_x28;
  puStack_3e8 = unaff_x27;
  local_3e0 = unaff_x26;
  puStack_3d8 = unaff_x25;
  local_3d0 = unaff_x24;
  puStack_3c8 = unaff_x23;
  local_3c0 = unaff_x22;
  uStack_3b8 = unaff_x21;
  local_3b0 = unaff_x20;
  puStack_3a8 = unaff_x19;
  local_3a0 = &stack0xfffffffffffffff0;
  if ((long)puVar11 < 4) {
LAB_1b709cc30:
    puVar12 = (uint *)0xffffffffffffffff;
    puVar11 = param_4;
LAB_1b709cc34:
    puVar27 = puVar12;
    param_4 = puVar11;
    auVar47 = auVar48;
    if (*_DAT_1e016af20 == local_400) {
      return puVar12;
    }
  }
  else {
    uVar26 = *puVar27;
    if ((uVar26 & 0x7f000000) != 0x61000000) {
      auVar48 = auVar47;
      if (uVar26 >> 0x18 != 0x24) goto LAB_1b709cc30;
      if ((uVar26 & 0x240000ff) == 0x24000000) {
        if ((uVar26 & 0xff00) != 0) {
          puVar41 = (ulong *)((ulong)(uVar26 >> 8) & 0xff);
          local_500[0] = puVar27[1];
          uVar22 = (ulong)local_500[0];
          local_700[0] = *(ulong *)(puVar27 + 2);
          puVar12 = (uint *)((long)puVar27 + uVar22 + 0x10);
          lVar13 = (long)puVar11 + (-0x10 - uVar22);
          uVar36 = local_700[0] + uVar22 +
                   (local_700[0] & ((long)local_700[0] >> 0x3f ^ 0xffffffffffffffffU));
          uVar36 = uVar36 & ((long)uVar36 >> 0x3f ^ 0xffffffffffffffffU);
          if ((int)puVar41 == 1) {
            puVar41 = (ulong *)0x1;
          }
          else {
            lVar23 = (long)puVar41 + -1;
            lVar14 = 1;
            uVar32 = local_700[0];
            do {
              uVar39 = (ulong)*puVar12;
              uVar33 = *(ulong *)(puVar12 + 1);
              local_500[lVar14] = *puVar12;
              local_700[lVar14] = uVar33;
              if ((long)uVar32 < (long)uVar33) {
                uVar32 = uVar33;
              }
              uVar32 = uVar32 + uVar33 + uVar39;
              if ((long)uVar36 <= (long)uVar32) {
                uVar36 = uVar32;
              }
              puVar12 = (uint *)((long)puVar12 + uVar39 + 0xc);
              lVar13 = (lVar13 - uVar39) + -0xc;
              lVar14 = lVar14 + 1;
              lVar23 = lVar23 + -1;
              uVar32 = uVar33;
            } while (lVar23 != 0);
          }
          puVar35 = (uint *)(lVar13 + -0xc);
          local_718 = param_4;
          puStack_710 = (uint *)param_3;
          unaff_x20 = func_0x0001b8120b80(uVar36,0x3065a8b);
          unaff_x22 = puVar12 + 3;
          unaff_x28 = puVar41;
          local_708 = puVar35;
          if ((long)puVar35 < 0) {
            unaff_x23 = puVar35;
            if (puVar41 != (ulong *)(ulong)*(byte *)((long)puVar27 + 1)) {
              unaff_x24 = (uint *)local_700[(long)puVar41];
              while( true ) {
                if (unaff_x28 == (ulong *)0x0) {
                  unaff_x25 = (uint *)(unaff_x20 +
                                      ((ulong)unaff_x24 &
                                      ((long)unaff_x24 >> 0x3f ^ 0xffffffffffffffffU)));
                  func_0x0001b8120bb0(unaff_x25,unaff_x22,uVar22);
                  func_0x0001b8120bb0((long)unaff_x25 + uVar22,unaff_x20,unaff_x24);
                  goto LAB_1b709cfe8;
                }
                unaff_x27 = (ulong *)((long)unaff_x28 + -1);
                unaff_x23 = (uint *)local_700[(long)unaff_x27];
                puVar11 = unaff_x24;
                if ((long)unaff_x24 <= (long)unaff_x23) {
                  puVar11 = unaff_x23;
                }
                unaff_x25 = (uint *)(unaff_x20 + (long)puVar11);
                unaff_x26 = (ulong *)(ulong)local_500[(long)unaff_x28];
                func_0x0001b8120bb0(unaff_x25,unaff_x22,unaff_x26);
                param_3 = (undefined1  [8])unaff_x24;
                func_0x0001b8120bb0((long)unaff_x25 + (long)unaff_x26,unaff_x20);
                puVar11 = (uint *)((long)unaff_x24 + (long)unaff_x26);
                if ((long)puVar11 < 0) break;
                param_6 = 8;
                param_3 = (undefined1  [8])unaff_x23;
                param_4 = unaff_x25;
                lVar13 = FUN_1b709d024(unaff_x20,0);
                if ((lVar13 < 0) ||
                   (unaff_x22 = (uint *)((long)unaff_x22 +
                                        (-0xc - (ulong)local_500[(long)unaff_x27])),
                   unaff_x24 = unaff_x23, unaff_x28 = unaff_x27,
                   unaff_x27 == (ulong *)(ulong)*(byte *)((long)puVar27 + 1))) break;
              }
            }
          }
          else {
            unaff_x27 = local_700;
            unaff_x23 = local_500;
            do {
              uVar22 = 0xfffffffffffffff4;
              if (unaff_x28 == (ulong *)(ulong)*(byte *)((long)puVar27 + 1)) {
                unaff_x26 = (ulong *)((long)puVar41 + -1);
                param_3 = (undefined1  [8])unaff_x27[(long)unaff_x26];
                param_6 = 8;
                param_4 = unaff_x22;
                puVar11 = local_708;
                lVar13 = FUN_1b709d024(unaff_x20,0);
                puVar12 = (uint *)0xffffffffffffffff;
                if ((unaff_x28 == (ulong *)0x0) || (lVar13 < 0)) goto LAB_1b709d00c;
              }
              else {
                if (unaff_x28 == (ulong *)0x0) {
                  puVar11 = (uint *)0x0;
                }
                else {
                  puVar11 = (uint *)unaff_x27[(long)puVar41 + -1];
                }
                unaff_x24 = (uint *)unaff_x27[(long)puVar41];
                puVar12 = unaff_x24;
                if ((long)unaff_x24 <= (long)puVar11) {
                  puVar12 = puVar11;
                }
                unaff_x25 = (uint *)(unaff_x20 + (long)puVar12);
                uVar22 = (ulong)unaff_x23[(long)puVar41];
                func_0x0001b8120bb0(unaff_x25,unaff_x22,uVar22);
                param_3 = (undefined1  [8])unaff_x24;
                func_0x0001b8120bb0((long)unaff_x25 + uVar22,unaff_x20);
                unaff_x26 = puVar41;
                if (unaff_x28 == (ulong *)0x0) goto LAB_1b709cfe8;
                puVar11 = (uint *)((long)unaff_x24 + uVar22);
                if ((long)puVar11 < 0) break;
                unaff_x26 = (ulong *)((long)puVar41 + -1);
                param_3 = (undefined1  [8])unaff_x27[(long)unaff_x26];
                param_6 = 8;
                param_4 = unaff_x25;
                lVar13 = FUN_1b709d024(unaff_x20,0);
                uVar22 = 0xfffffffffffffff4;
                if (lVar13 < 0) break;
              }
              puVar41 = (ulong *)((long)puVar41 + -1);
              uVar22 = 0xfffffffffffffff4;
              unaff_x22 = (uint *)((long)unaff_x22 + (-0xc - (ulong)unaff_x23[(long)puVar41]));
              puVar42 = (ulong *)((long)unaff_x28 + -1);
              bVar10 = 0 < (long)unaff_x28;
              unaff_x26 = puVar41;
              unaff_x28 = puVar42;
            } while (bVar10);
          }
LAB_1b709d008:
          puVar12 = (uint *)0xffffffffffffffff;
LAB_1b709d00c:
          func_0x0001b81206e0(unaff_x20);
          auVar48._8_8_ = puVar11;
          auVar48._0_8_ = puVar12;
          puVar11 = param_4;
          unaff_x21 = uVar22;
          goto LAB_1b709cc34;
        }
        auVar48._8_8_ = puVar11 + -4;
        auVar48._0_8_ = puVar27;
        if (puVar11 < (uint *)0x10) goto LAB_1b709cc30;
        auVar47._8_8_ = puVar11 + -4;
        auVar47._0_8_ = puVar27 + 4;
      }
      param_6 = 0x10;
      puVar12 = (uint *)FUN_1b709d024(0,param_3);
      puVar11 = auVar47._0_8_;
      auVar48._8_8_ = auVar47._8_8_;
      auVar48._0_8_ = puVar27;
      param_3 = (undefined1  [8])param_4;
      goto LAB_1b709cc34;
    }
    if (*_DAT_1e016af20 == local_400) {
      puVar11 = (uint *)FUN_1b709d024(0,param_3,param_4,puVar27,puVar11,0x10);
      return puVar11;
    }
  }
  uVar36 = auVar47._8_8_;
  func_0x0001b811fac0(puVar27);
  pcStack_728 = FUN_1b709d024;
  puStack_780 = unaff_x28;
  puStack_778 = unaff_x27;
  puStack_770 = unaff_x26;
  puStack_768 = unaff_x25;
  puStack_760 = unaff_x24;
  puStack_758 = unaff_x23;
  puStack_750 = unaff_x22;
  uStack_748 = unaff_x21;
  lStack_740 = unaff_x20;
  uStack_738 = auVar47._0_8_;
  ppuStack_730 = &local_3a0;
  auVar48 = (*_DAT_1e8d38a30)();
  lVar13 = auVar48._8_8_;
  lVar14 = auVar48._0_8_;
  lStack_790 = *_DAT_1e016af20;
  uStack_47a8 = 0;
  uStack_47b0 = 0;
  uStack_4798 = 0;
  uStack_47a0 = 0;
  iVar17 = (int)param_6;
  uStack_47c8 = 0;
  uStack_47d0 = 0;
  uStack_47b8 = 0;
  uStack_47c0 = 0;
  iVar19 = 0xc;
  if (iVar17 == 8) {
    iVar19 = 0xd;
  }
  uStack_47e8 = 0;
  uStack_47f0 = 0;
  uStack_47d8 = 0;
  uStack_47e0 = 0;
  uStack_4808 = 0;
  uStack_4810 = 0;
  uStack_47f8 = 0;
  uStack_4800 = 0;
  puVar11 = (uint *)param_3;
  if (uVar36 == 0) {
joined_r0x0001b709d0e4:
    if (puVar11 == (uint *)0x0) goto LAB_1b709d0ec;
  }
  else {
    puVar11 = (uint *)(uVar36 - 4);
    if (3 < uVar36) {
      puVar27 = param_4 + 1;
      uVar25 = *param_4;
      uVar26 = uVar25 & 0x800000ff;
      bVar10 = (uVar25 & 0x7f000000) != 0x61000000;
      if (bVar10) {
        uVar26 = 0xffffffff;
      }
      if ((!bVar10 && (int)uVar26 < 3) && (uVar26 & 0x7ffffffe) != 0) {
        if ((param_3 == (undefined1  [8])0x0) || (puVar11 == (uint *)0x0)) {
          if (param_3 == (undefined1  [8])puVar11) goto LAB_1b709d0ec;
        }
        else if ((int)uVar25 < 0) {
          lVar23 = (long)param_3 << (lVar14 == 0);
          if (uVar36 == lVar23 + 4U) {
            if (lVar14 != 0) {
              lVar13 = lVar14;
            }
            func_0x0001b8120bb0(lVar13,puVar27,lVar23);
            goto LAB_1b709d0ec;
          }
        }
        else {
          if (puVar11 < (uint *)0x4) {
            lVar31 = 0;
          }
          else {
            auStack_4830 = (undefined1  [8])
                           (((ulong)param_4[1] << 0x20) >> ((ulong)(uint)-iVar17 & 0x3f));
            puVar12 = param_4 + 2;
            lVar38 = uVar36 - 8;
            auStack_4818 = (undefined1  [8])(param_6 & 0xffffffff);
            auStack_4820 = (undefined1  [8])(ulong)(0x40 - iVar17);
            uVar22 = ((ulong)param_4[1] << 0x20) << (param_6 & 0x3f);
            uVar26 = SUB84(auStack_4830,0) + 1;
            uVar32 = (ulong)uVar26;
            uVar39 = uVar22 >> 0x3d;
            iVar21 = 0x1d - iVar17;
            uVar33 = uVar22 << 3;
            auStack_4828 = param_3;
            lVar31 = func_0x0001b8120b80(uVar32 << 3,0x100004000313f17);
            auVar24 = auStack_4830;
            iVar20 = 0;
            lVar23 = 0;
            uVar25 = (uint)(param_6 >> 1) & 0x7fffffff;
            uVar36 = uVar32;
            do {
              if (uVar39 == 0) {
                puVar35 = (uint *)(lVar31 + lVar23 * 8);
                lVar37 = lVar38;
                if (uVar26 == 2) {
                  *(undefined2 *)(puVar35 + 1) = 1;
                  if (iVar21 < 1) {
                    lVar37 = lVar38 + -4;
                    if (lVar38 < 4) {
                      uVar29 = 0;
                    }
                    else {
                      uVar29 = (ulong)*puVar12;
                      puVar12 = puVar12 + 1;
                    }
                    uVar33 = uVar29 << ((ulong)(0x20 - iVar21) & 0x3f) | uVar33;
                    iVar21 = iVar21 + 0x20;
                  }
                  iVar40 = iVar21 + -1;
                  uVar34 = uVar33 << 1;
                  *puVar35 = (uint)(uVar33 >> 0x3f);
                }
                else {
                  *puVar35 = 0;
                  *(undefined2 *)(puVar35 + 1) = 0;
                  uVar34 = uVar33;
                  iVar40 = iVar21;
                }
              }
              else {
                uVar4 = (uint)(uVar22 >> 0x20);
                lVar30 = lVar38;
                if (iVar21 < (int)(uVar4 >> 0x1d)) {
                  lVar30 = lVar38 + -4;
                  if (lVar38 < 4) {
                    uVar29 = 0;
                  }
                  else {
                    uVar29 = (ulong)*puVar12;
                    puVar12 = puVar12 + 1;
                  }
                  uVar33 = uVar29 << ((ulong)(0x20 - iVar21) & 0x3f) | uVar33;
                  iVar21 = iVar21 + 0x20;
                }
                iVar21 = iVar21 - (uVar4 >> 0x1d);
                uVar29 = uVar33 << uVar39;
                uVar4 = (int)(uVar33 >> (0x40 - uVar39 & 0x3f)) + 1;
                puVar1 = (undefined4 *)(lVar31 + lVar23 * 8);
                *(short *)(puVar1 + 1) = (short)uVar4;
                uVar4 = uVar4 & 0xffff;
                lVar37 = lVar30;
                if (iVar21 < (int)uVar4) {
                  lVar37 = lVar30 + -4;
                  if (lVar30 < 4) {
                    uVar33 = 0;
                  }
                  else {
                    uVar33 = (ulong)*puVar12;
                    puVar12 = puVar12 + 1;
                  }
                  uVar29 = uVar33 << ((ulong)(0x20 - iVar21) & 0x3f) | uVar29;
                  iVar21 = iVar21 + 0x20;
                }
                iVar40 = iVar21 - uVar4;
                uVar34 = uVar29 << ((ulong)uVar4 & 0x3f);
                *puVar1 = (int)(uVar29 >> ((ulong)-uVar4 & 0x3f));
              }
              lVar38 = lVar37;
              if (iVar40 < 1) {
                lVar38 = lVar37 + -4;
                if (lVar37 < 4) {
                  uVar33 = 0;
                }
                else {
                  uVar33 = (ulong)*puVar12;
                  puVar12 = puVar12 + 1;
                }
                uVar34 = uVar33 << ((ulong)(0x20 - iVar40) & 0x3f) | uVar34;
                iVar40 = iVar40 + 0x20;
              }
              iVar21 = iVar40 + -1;
              uVar33 = uVar34 << 1;
              if ((long)uVar34 < 0) {
                lVar30 = lVar38;
                if (iVar40 < 2) {
                  lVar30 = lVar38 + -4;
                  if (lVar38 < 4) {
                    uVar29 = 0;
                  }
                  else {
                    uVar29 = (ulong)*puVar12;
                    puVar12 = puVar12 + 1;
                  }
                  uVar33 = uVar29 << ((ulong)(0x21 - iVar40) & 0x3f) | uVar33;
                  iVar21 = iVar40 + 0x1f;
                }
                iVar40 = iVar21 + -1;
                uVar29 = uVar33 << 1;
                lVar38 = lVar30;
                if ((long)uVar33 < 0) {
                  if (iVar21 <= iVar17) {
                    lVar38 = lVar30 + -4;
                    if (lVar30 < 4) {
                      uVar33 = 0;
                    }
                    else {
                      uVar33 = (ulong)*puVar12;
                      puVar12 = puVar12 + 1;
                    }
                    uVar29 = uVar33 << ((ulong)(0x21 - iVar21) & 0x3f) | uVar29;
                    iVar40 = iVar21 + 0x1f;
                  }
                  iVar20 = (int)(uVar29 >> ((ulong)auStack_4820 & 0x3f));
                  iVar21 = iVar40 - iVar17;
                  uVar33 = uVar29 << ((ulong)auStack_4818 & 0x3f);
                }
                else {
                  puVar35 = puVar12;
                  if (iVar21 <= (int)uVar25) {
                    lVar38 = lVar30 + -4;
                    if (lVar30 < 4) {
                      uVar33 = 0;
                    }
                    else {
                      puVar35 = puVar12 + 1;
                      uVar33 = (ulong)*puVar12;
                    }
                    uVar29 = uVar33 << ((ulong)(0x21 - iVar21) & 0x3f) | uVar29;
                    iVar40 = iVar21 + 0x1f;
                  }
                  iVar21 = iVar40 - uVar25;
                  uVar33 = uVar29 << (param_6 >> 1 & 0x3f);
                  iVar20 = iVar20 + (int)(uVar29 >> ((ulong)(0x40 - uVar25) & 0x3f));
                  puVar12 = puVar35;
                }
              }
              *(short *)(lVar31 + lVar23 * 8 + 6) = (short)iVar20;
              iVar20 = iVar20 + 1;
              lVar23 = lVar23 + 1;
              uVar36 = uVar36 - 1;
            } while (uVar36 != 0);
            if (-1 < lVar38) {
              puVar35 = (uint *)((long)puVar27 + ((long)puVar12 - (long)puVar27));
              uVar36 = (long)puVar11 - ((long)puVar12 - (long)puVar27);
              if (-1 < (long)uVar36) {
                uVar22 = 0;
                uVar33 = 0;
                do {
                  iVar20 = (int)uVar33;
                  if (0 < iVar20) {
                    uVar39 = 0;
                    uVar5 = *(ushort *)(lVar31 + uVar22 * 8 + 4);
                    uVar26 = (uint)uVar5;
                    uVar29 = uVar33;
LAB_1b709d474:
                    uVar25 = *(uint *)((long)&uStack_4810 + uVar39 * 4);
                    if (uVar25 != uVar5) {
                      if ((int)uVar25 < (int)(uint)uVar5) goto code_r0x0001b709d484;
                      uVar25 = (uint)uVar39;
                      if (iVar20 <= (int)uVar25) goto LAB_1b709d520;
                      uVar34 = uVar33 - uVar39;
                      if (uVar34 < 8) goto LAB_1b709d504;
                      lVar23 = 0;
                      uVar29 = uVar29 & 0xfffffffffffffff8;
                      do {
                        lVar30 = (uVar33 - lVar23) * 4;
                        uVar44 = *(undefined8 *)(auStack_4820 + lVar30);
                        uVar46 = *(undefined8 *)(auStack_4828 + lVar30);
                        uVar45 = *(undefined8 *)(auStack_4830 + lVar30);
                        lVar38 = (uVar33 - lVar23) * 4;
                        *(undefined8 *)(auStack_4818 + lVar38 + 4) =
                             *(undefined8 *)(auStack_4818 + lVar30);
                        *(undefined8 *)(auStack_4820 + lVar38 + 4) = uVar44;
                        *(undefined8 *)(auStack_4828 + lVar38 + 4) = uVar46;
                        *(undefined8 *)(auStack_4830 + lVar38 + 4) = uVar45;
                        lVar23 = lVar23 + 8;
                        uVar29 = uVar29 - 8;
                      } while (uVar29 != 0);
                      if (uVar34 != (uVar34 & 0xfffffffffffffff8)) {
                        uVar33 = uVar33 - (uVar34 & 0xfffffffffffffff8);
LAB_1b709d504:
                        do {
                          uVar29 = uVar33 - 1;
                          *(undefined4 *)((long)&uStack_4810 + uVar33 * 4) =
                               *(undefined4 *)((long)&uStack_4810 + uVar29 * 4);
                          uVar33 = uVar29;
                        } while ((long)(int)uVar25 < (long)uVar29);
                      }
LAB_1b709d520:
                      *(uint *)((long)&uStack_4810 + uVar39 * 4) = uVar26;
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
                    uVar26 = (uint)*(ushort *)(lVar31 + uVar22 * 8 + 4);
LAB_1b709d444:
                    uVar33 = (ulong)(iVar20 + 1);
                    *(uint *)((long)&uStack_4810 + (long)iVar20 * 4) = uVar26;
                  }
LAB_1b709d44c:
                  bVar10 = (undefined1  [8])uVar22 != auVar24;
                  uVar22 = uVar22 + 1;
                } while (bVar10);
                iVar21 = (int)uVar33;
                uVar22 = (long)iVar21 - 1;
                iVar20 = *(int *)((long)&uStack_4810 + uVar22 * 4);
                if (iVar21 < 1) {
                  uVar26 = 0;
                  iVar40 = 0;
                  if (iVar21 != 0) {
                    iVar40 = iVar19;
                  }
                }
                else {
                  do {
                    iVar40 = *(int *)((long)&uStack_4810 + (uVar22 & 0xffffffff) * 4);
                    if (iVar40 <= iVar19) goto LAB_1b709d570;
                    uVar26 = (int)uVar22 - 1;
                    uVar22 = (ulong)uVar26;
                  } while (uVar26 != 0xffffffff);
                  iVar40 = 0;
LAB_1b709d570:
                  lVar23 = 0;
                  uVar26 = 0;
                  do {
                    iVar19 = *(int *)((long)&uStack_4810 + lVar23 * 4);
                    if (iVar40 < iVar19) {
                      *(int *)((long)&uStack_4810 + (long)(int)uVar26 * 4) = iVar19;
                      uVar26 = uVar26 + 1;
                    }
                    lVar23 = lVar23 + 1;
                    uVar33 = uVar33 - 1;
                  } while (uVar33 != 0);
                }
                if (iVar17 == 8) {
                  func_0x0001b811fc60(auStack_4790,0x4000);
                  if (auVar24 == (undefined1  [8])0x0) {
                    if (0 < (long)auStack_4828) {
                      func_0x0001b8120bd0(lVar14,*(undefined1 *)(lVar31 + 6),auStack_4828);
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
                  uVar4 = uVar25;
                  if (uVar25 < 2) {
                    uVar4 = 1;
                  }
                  do {
                    piVar2 = (int *)(lVar31 + uVar22 * 8);
                    uVar5 = *(ushort *)(piVar2 + 1);
                    uVar43 = iVar40 - (uint)uVar5;
                    if (iVar40 < (int)(uint)uVar5) {
                      uVar15 = *piVar2 << (ulong)(iVar20 - (uint)uVar5 & 0x1f);
                      uVar43 = (uVar15 ^ uVar15 >> 0x10) * -0x7a143595;
                      uVar43 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                      uVar43 = uVar43 ^ uVar43 >> 0x10;
                      uVar28 = uVar4;
                      do {
                        uVar18 = 0;
                        if (uVar25 != 0) {
                          uVar18 = uVar43 / uVar25;
                        }
                        uVar43 = uVar43 - uVar18 * uVar25;
                        if (*(int *)(lVar13 + (ulong)uVar43 * 8 + 4) == 0) {
                          iVar19 = iVar19 + 1;
                          puVar11 = (uint *)(lVar13 + (ulong)uVar43 * 8);
                          *puVar11 = uVar15;
                          puVar11[1] = (int)uVar22 + 1;
                          break;
                        }
                        uVar43 = uVar43 + 1;
                        uVar28 = uVar28 - 1;
                      } while (uVar28 != 0);
                    }
                    else {
                      uVar28 = *piVar2 << (ulong)(uVar43 & 0x1f);
                      uVar5 = *(ushort *)((long)piVar2 + 6) | uVar5 << 8;
                      *(ushort *)((long)auStack_4790 + (ulong)uVar28 * 2) = uVar5;
                      uVar15 = 1;
                      do {
                        *(ushort *)((long)auStack_4790 + (ulong)((uVar28 + uVar15) - 1) * 2) = uVar5
                        ;
                        uVar18 = uVar15 >> (ulong)(uVar43 & 0x1f);
                        uVar15 = uVar15 + 1;
                      } while (uVar18 == 0);
                    }
                    uVar22 = uVar22 + 1;
                  } while (uVar22 != uVar32);
                  if (iVar40 < iVar20) {
                    if (0 < (long)auStack_4828) {
                      auStack_4820._0_4_ = iVar19;
                      iVar19 = 0;
                      puVar11 = (uint *)0x0;
                      puVar27 = (uint *)0x0;
                      uVar22 = uVar36;
LAB_1b709d7d4:
                      if (iVar40 < 1) {
LAB_1b709d824:
                        uVar36 = uVar22;
                        if (iVar19 < iVar20) {
                          uVar36 = uVar22 - 4;
                          if ((long)uVar22 < 4) {
                            uVar22 = 0;
                          }
                          else {
                            uVar22 = (ulong)*puVar35;
                            puVar35 = puVar35 + 1;
                          }
                          puVar11 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                            (ulong)puVar11);
                          iVar19 = iVar19 + 0x20;
                        }
                        uVar18 = (uint)((ulong)puVar11 >> ((ulong)(0x40 - iVar20) & 0x3f));
                        uVar43 = (uVar18 ^ uVar18 >> 0x10) * -0x7a143595;
                        uVar15 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                        uVar15 = uVar15 ^ uVar15 >> 0x10;
                        uVar28 = uVar4;
                        uVar43 = uVar15;
                        do {
                          uVar7 = 0;
                          if (uVar25 != 0) {
                            uVar7 = uVar43 / uVar25;
                          }
                          uVar43 = uVar43 - uVar7 * uVar25;
                          puVar12 = (uint *)(lVar13 + (ulong)uVar43 * 8);
                          uVar7 = puVar12[1];
                          if (*puVar12 == uVar18) {
                            iVar17 = uVar7 - 1;
                            goto LAB_1b709d8a4;
                          }
                          if (uVar7 == 0) break;
                          uVar43 = uVar43 + 1;
                          uVar28 = uVar28 - 1;
                        } while (uVar28 != 0);
                        iVar17 = -1;
LAB_1b709d8a4:
                        if ((0 < (int)uVar26) && (iVar17 == -1)) {
                          auStack_4818 = (undefined1  [8])uVar36;
                          uVar22 = 0;
                          do {
                            uVar7 = *(uint *)((long)&uStack_4810 + uVar22 * 4);
                            uVar28 = -1 << (ulong)(iVar20 - uVar7 & 0x1f) & uVar18;
                            uVar43 = (uVar28 ^ uVar28 >> 0x10) * -0x7a143595;
                            uVar43 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                            uVar43 = uVar43 ^ uVar43 >> 0x10;
                            uVar16 = uVar25;
                            do {
                              uVar8 = 0;
                              if (uVar25 != 0) {
                                uVar8 = uVar43 / uVar25;
                              }
                              uVar43 = uVar43 - uVar8 * uVar25;
                              puVar12 = (uint *)(lVar13 + (ulong)uVar43 * 8);
                              uVar8 = puVar12[1];
                              if (*puVar12 == uVar28) {
                                if ((uVar8 != 0) &&
                                   (iVar17 = uVar8 - 1,
                                   uVar7 == *(ushort *)(lVar31 + (long)iVar17 * 8 + 4))) {
                                  uVar43 = uVar25;
                                  if (uVar25 <= (uint)(auStack_4820._0_4_ * 2)) goto LAB_1b709d7b0;
                                  goto LAB_1b709d958;
                                }
                                break;
                              }
                              if (uVar8 == 0) break;
                              uVar43 = uVar43 + 1;
                              uVar16 = uVar16 - 1;
                            } while (uVar16 != 0);
                            uVar22 = uVar22 + 1;
                          } while (uVar22 != uVar26);
                          iVar17 = -1;
                        }
                        goto LAB_1b709d7b0;
                      }
                      uVar36 = uVar22;
                      if (iVar19 < iVar40) {
                        uVar36 = uVar22 - 4;
                        if ((long)uVar22 < 4) {
                          uVar22 = 0;
                        }
                        else {
                          uVar22 = (ulong)*puVar35;
                          puVar35 = puVar35 + 1;
                        }
                        puVar11 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                          (ulong)puVar11);
                        iVar19 = iVar19 + 0x20;
                      }
                      uVar5 = *(ushort *)
                               ((long)auStack_4790 +
                               ((ulong)puVar11 >> ((ulong)(0x40 - iVar40) & 0x3f)) * 2);
                      uVar22 = uVar36;
                      if (uVar5 == 0) goto LAB_1b709d824;
                      *(char *)(lVar14 + (long)puVar27) = (char)uVar5;
                      uVar5 = uVar5 >> 8;
                      goto LAB_1b709d7c0;
                    }
LAB_1b709ddf0:
                    puVar11 = (uint *)0x0;
LAB_1b709ddf4:
                    func_0x0001b81206e0();
                  }
                  else {
                    if ((long)auStack_4828 < 1) goto LAB_1b709de84;
                    puVar11 = (uint *)0x0;
                    iVar19 = 0;
                    lVar13 = 0;
                    auVar24 = auStack_4828;
                    uVar22 = uVar36;
                    do {
                      uVar36 = uVar22;
                      puVar27 = puVar35;
                      if (iVar19 < iVar40) {
                        uVar36 = uVar22 - 4;
                        if ((long)uVar22 < 4) {
                          uVar22 = 0;
                        }
                        else {
                          puVar27 = puVar35 + 1;
                          uVar22 = (ulong)*puVar35;
                        }
                        puVar11 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                          (ulong)puVar11);
                        iVar19 = iVar19 + 0x20;
                      }
                      uVar5 = *(ushort *)
                               ((long)auStack_4790 +
                               ((ulong)puVar11 >> ((ulong)(0x40 - iVar40) & 0x3f)) * 2);
                      *(char *)(lVar14 + lVar13) = (char)uVar5;
                      uVar5 = uVar5 >> 8;
                      iVar19 = iVar19 - (uint)uVar5;
                      puVar11 = (uint *)((long)puVar11 << ((ulong)uVar5 & 0x3f));
                      lVar13 = lVar13 + 1;
                      auVar24 = (undefined1  [8])((long)auVar24 + -1);
                      uVar22 = uVar36;
                      puVar35 = puVar27;
                    } while (auVar24 != (undefined1  [8])0x0);
                  }
                }
                else {
                  func_0x0001b811fc60(auStack_4790,0x4000);
                  if (auVar24 == (undefined1  [8])0x0) {
                    if (0 < (long)auStack_4828) {
                      uVar6 = *(undefined2 *)(lVar31 + 6);
                      if ((ulong)auStack_4828 < (uint *)0x4) {
                        puVar11 = (uint *)0x0;
                      }
                      else {
                        if ((ulong)auStack_4828 < (uint *)0x10) {
                          puVar27 = (uint *)0x0;
                        }
                        else {
                          lVar14 = 0;
                          puVar11 = (uint *)((ulong)auStack_4828 & 0x7ffffffffffffff0);
                          uVar44 = CONCAT26(uVar6,CONCAT24(uVar6,CONCAT22(uVar6,uVar6)));
                          uVar45 = CONCAT26(uVar6,CONCAT24(uVar6,CONCAT22(uVar6,uVar6)));
                          puVar27 = puVar11;
                          do {
                            puVar3 = (undefined8 *)(lVar13 + lVar14 * 2);
                            puVar3[1] = uVar45;
                            *puVar3 = uVar44;
                            puVar3[3] = uVar45;
                            puVar3[2] = uVar44;
                            lVar14 = lVar14 + 0x10;
                            puVar27 = puVar27 + -4;
                          } while (puVar27 != (uint *)0x0);
                          if (auStack_4828 == (undefined1  [8])puVar11) goto LAB_1b709de84;
                          puVar27 = puVar11;
                          if (((ulong)auStack_4828 & 0xc) == 0) goto LAB_1b709de70;
                        }
                        puVar11 = (uint *)((ulong)auStack_4828 & 0x7ffffffffffffffc);
                        lVar14 = (long)puVar27 - (long)puVar11;
                        do {
                          *(ulong *)(lVar13 + (long)puVar27 * 2) =
                               CONCAT26(uVar6,CONCAT24(uVar6,CONCAT22(uVar6,uVar6)));
                          puVar27 = puVar27 + 1;
                          lVar14 = lVar14 + 4;
                        } while (lVar14 != 0);
                        if (auStack_4828 == (undefined1  [8])puVar11) goto LAB_1b709de84;
                      }
LAB_1b709de70:
                      lVar14 = (long)auStack_4828 - (long)puVar11;
                      do {
                        *(undefined2 *)(lVar13 + (long)puVar11 * 2) = uVar6;
                        puVar11 = (uint *)((long)puVar11 + 1);
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
                    uVar4 = uVar25;
                    if (uVar25 < 2) {
                      uVar4 = 1;
                    }
                    do {
                      piVar2 = (int *)(lVar31 + uVar22 * 8);
                      uVar5 = *(ushort *)(piVar2 + 1);
                      uVar43 = iVar40 - (uint)uVar5;
                      if (iVar40 < (int)(uint)uVar5) {
                        uVar15 = *piVar2 << (ulong)(iVar20 - (uint)uVar5 & 0x1f);
                        uVar43 = (uVar15 ^ uVar15 >> 0x10) * -0x7a143595;
                        uVar43 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                        uVar43 = uVar43 ^ uVar43 >> 0x10;
                        uVar28 = uVar4;
                        do {
                          uVar18 = 0;
                          if (uVar25 != 0) {
                            uVar18 = uVar43 / uVar25;
                          }
                          uVar43 = uVar43 - uVar18 * uVar25;
                          if (*(int *)(lVar14 + (ulong)uVar43 * 8 + 4) == 0) {
                            iVar19 = iVar19 + 1;
                            puVar11 = (uint *)(lVar14 + (ulong)uVar43 * 8);
                            *puVar11 = uVar15;
                            puVar11[1] = (int)uVar22 + 1;
                            break;
                          }
                          uVar43 = uVar43 + 1;
                          uVar28 = uVar28 - 1;
                        } while (uVar28 != 0);
                      }
                      else {
                        uVar28 = *piVar2 << (ulong)(uVar43 & 0x1f);
                        uVar18 = CONCAT22(uVar5,*(undefined2 *)((long)piVar2 + 6));
                        auStack_4790[uVar28] = uVar18;
                        uVar15 = 1;
                        do {
                          auStack_4790[(uVar28 + uVar15) - 1] = uVar18;
                          uVar7 = uVar15 >> (ulong)(uVar43 & 0x1f);
                          uVar15 = uVar15 + 1;
                        } while (uVar7 == 0);
                      }
                      uVar22 = uVar22 + 1;
                    } while (uVar22 != uVar32);
                    if (iVar40 < iVar20) {
                      if (0 < (long)auStack_4828) {
                        auStack_4820._0_4_ = iVar19;
                        iVar19 = 0;
                        puVar11 = (uint *)0x0;
                        puVar27 = (uint *)0x0;
                        uVar22 = uVar36;
LAB_1b709dad8:
                        puVar12 = puVar35;
                        if (iVar40 < 1) {
LAB_1b709db3c:
                          uVar36 = uVar22;
                          if (iVar19 < iVar20) {
                            uVar36 = uVar22 - 4;
                            if ((long)uVar22 < 4) {
                              uVar22 = 0;
                            }
                            else {
                              uVar22 = (ulong)*puVar12;
                              puVar12 = puVar12 + 1;
                            }
                            puVar11 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                              (ulong)puVar11);
                            iVar19 = iVar19 + 0x20;
                          }
                          uVar18 = (uint)((ulong)puVar11 >> ((ulong)(0x40 - iVar20) & 0x3f));
                          uVar43 = (uVar18 ^ uVar18 >> 0x10) * -0x7a143595;
                          uVar15 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                          uVar15 = uVar15 ^ uVar15 >> 0x10;
                          uVar28 = uVar4;
                          uVar43 = uVar15;
                          do {
                            uVar7 = 0;
                            if (uVar25 != 0) {
                              uVar7 = uVar43 / uVar25;
                            }
                            uVar43 = uVar43 - uVar7 * uVar25;
                            puVar35 = (uint *)(lVar14 + (ulong)uVar43 * 8);
                            uVar7 = puVar35[1];
                            if (*puVar35 == uVar18) {
                              iVar17 = uVar7 - 1;
                              goto LAB_1b709dbbc;
                            }
                            if (uVar7 == 0) break;
                            uVar43 = uVar43 + 1;
                            uVar28 = uVar28 - 1;
                          } while (uVar28 != 0);
                          iVar17 = -1;
LAB_1b709dbbc:
                          if ((0 < (int)uVar26) && (iVar17 == -1)) {
                            auStack_4818 = (undefined1  [8])uVar36;
                            uVar22 = 0;
                            do {
                              uVar7 = *(uint *)((long)&uStack_4810 + uVar22 * 4);
                              uVar28 = -1 << (ulong)(iVar20 - uVar7 & 0x1f) & uVar18;
                              uVar43 = (uVar28 ^ uVar28 >> 0x10) * -0x7a143595;
                              uVar43 = (uVar43 ^ uVar43 >> 0xd) * -0x3d4d51cb;
                              uVar43 = uVar43 ^ uVar43 >> 0x10;
                              uVar16 = uVar25;
                              do {
                                uVar8 = 0;
                                if (uVar25 != 0) {
                                  uVar8 = uVar43 / uVar25;
                                }
                                uVar43 = uVar43 - uVar8 * uVar25;
                                puVar35 = (uint *)(lVar14 + (ulong)uVar43 * 8);
                                uVar8 = puVar35[1];
                                if (*puVar35 == uVar28) {
                                  if ((uVar8 != 0) &&
                                     (iVar17 = uVar8 - 1,
                                     uVar7 == *(ushort *)(lVar31 + (long)iVar17 * 8 + 4))) {
                                    uVar43 = uVar25;
                                    if (uVar25 <= (uint)(auStack_4820._0_4_ * 2))
                                    goto LAB_1b709dcb0;
                                    goto LAB_1b709dc70;
                                  }
                                  break;
                                }
                                if (uVar8 == 0) break;
                                uVar43 = uVar43 + 1;
                                uVar16 = uVar16 - 1;
                              } while (uVar16 != 0);
                              uVar22 = uVar22 + 1;
                            } while (uVar22 != uVar26);
                            iVar17 = -1;
                          }
                          goto LAB_1b709dcb0;
                        }
                        uVar36 = uVar22;
                        if (iVar19 < iVar40) {
                          uVar36 = uVar22 - 4;
                          if ((long)uVar22 < 4) {
                            uVar22 = 0;
                          }
                          else {
                            uVar22 = (ulong)*puVar35;
                            puVar35 = puVar35 + 1;
                          }
                          puVar11 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                            (ulong)puVar11);
                          iVar19 = iVar19 + 0x20;
                        }
                        uVar43 = auStack_4790[(ulong)puVar11 >> ((ulong)(0x40 - iVar40) & 0x3f)];
                        uVar22 = uVar36;
                        puVar12 = puVar35;
                        if (uVar43 == 0) goto LAB_1b709db3c;
                        *(short *)(lVar13 + (long)puVar27 * 2) = (short)uVar43;
                        uVar22 = (ulong)(uVar43 >> 0x10);
                        if (iVar19 < (int)(uVar43 >> 0x10)) {
                          if ((long)uVar36 < 4) {
                            uVar32 = 0;
                          }
                          else {
                            uVar32 = (ulong)*puVar35;
                            puVar35 = puVar35 + 1;
                          }
                          puVar11 = (uint *)(uVar32 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                            (ulong)puVar11);
                          goto LAB_1b709dac0;
                        }
                        goto LAB_1b709dac4;
                      }
                      goto LAB_1b709ddf0;
                    }
                    if (0 < (long)auStack_4828) {
                      puVar11 = (uint *)0x0;
                      iVar19 = 0;
                      lVar14 = 0;
                      auVar24 = auStack_4828;
                      uVar22 = uVar36;
                      do {
                        uVar36 = uVar22;
                        puVar27 = puVar35;
                        if (iVar19 < iVar40) {
                          uVar36 = uVar22 - 4;
                          if ((long)uVar22 < 4) {
                            uVar22 = 0;
                          }
                          else {
                            puVar27 = puVar35 + 1;
                            uVar22 = (ulong)*puVar35;
                          }
                          puVar11 = (uint *)(uVar22 << ((ulong)(0x20 - iVar19) & 0x3f) |
                                            (ulong)puVar11);
                          iVar19 = iVar19 + 0x20;
                        }
                        uVar26 = auStack_4790[(ulong)puVar11 >> ((ulong)(0x40 - iVar40) & 0x3f)];
                        *(short *)(lVar13 + lVar14 * 2) = (short)uVar26;
                        uVar26 = uVar26 >> 0x10;
                        iVar19 = iVar19 - uVar26;
                        puVar11 = (uint *)((long)puVar11 << ((ulong)uVar26 & 0x3f));
                        lVar14 = lVar14 + 1;
                        auVar24 = (undefined1  [8])((long)auVar24 + -1);
                        uVar22 = uVar36;
                        puVar35 = puVar27;
                      } while (auVar24 != (undefined1  [8])0x0);
                      goto LAB_1b709de88;
                    }
                  }
LAB_1b709de84:
                  puVar11 = (uint *)0x0;
                }
LAB_1b709de88:
                if (0xfffffffffffffffa < uVar36 - 1) {
                  if (uVar36 != 0xfffffffffffffffc) {
                    func_0x0001b81206e0(lVar31);
                    param_3 = auStack_4828;
                    goto LAB_1b709d0ec;
                  }
                  func_0x0001b81206e0(lVar31);
                  param_3 = auStack_4828;
                  goto joined_r0x0001b709d0e4;
                }
              }
            }
          }
          func_0x0001b81206e0(lVar31);
        }
      }
    }
  }
  param_3 = (undefined1  [8])(uint *)0xffffffffffffffff;
LAB_1b709d0ec:
  if (*_DAT_1e016af20 != lStack_790) {
    func_0x0001b811fac0();
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  return (uint *)param_3;
}

