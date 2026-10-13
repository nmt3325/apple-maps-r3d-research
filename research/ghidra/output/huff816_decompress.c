
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_1b709d024(undefined8 param_1,undefined8 param_2,ulong param_3,uint *param_4,ulong param_5,
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
  bool bVar9;
  long lVar10;
  long lVar11;
  uint uVar12;
  undefined1 auVar13 [8];
  uint uVar14;
  int iVar15;
  uint uVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  ulong uVar20;
  long lVar21;
  ulong uVar22;
  uint uVar23;
  uint uVar24;
  uint uVar25;
  ulong uVar26;
  long lVar27;
  long lVar28;
  ulong uVar29;
  ulong uVar30;
  ulong uVar31;
  ulong uVar32;
  uint *puVar33;
  uint *puVar34;
  uint *puVar35;
  long lVar36;
  long lVar37;
  ulong uVar38;
  int iVar39;
  uint uVar40;
  undefined8 uVar41;
  undefined8 uVar42;
  undefined8 uVar43;
  undefined1 auVar44 [16];
  undefined1 local_4110 [8];
  undefined1 local_4108 [8];
  undefined1 local_4100 [8];
  undefined1 local_40f8 [8];
  undefined8 local_40f0;
  undefined8 uStack_40e8;
  undefined8 uStack_40e0;
  undefined8 uStack_40d8;
  undefined8 local_40d0;
  undefined8 uStack_40c8;
  undefined8 uStack_40c0;
  undefined8 uStack_40b8;
  undefined8 local_40b0;
  undefined8 uStack_40a8;
  undefined8 uStack_40a0;
  undefined8 uStack_4098;
  undefined8 local_4090;
  undefined8 uStack_4088;
  undefined8 uStack_4080;
  undefined8 uStack_4078;
  uint local_4070 [4096];
  long local_70;
  
  auVar44 = (*_DAT_1e8d38a30)();
  lVar10 = auVar44._8_8_;
  lVar11 = auVar44._0_8_;
  local_70 = *_DAT_1e016af20;
  uStack_4088 = 0;
  local_4090 = 0;
  uStack_4078 = 0;
  uStack_4080 = 0;
  iVar15 = (int)param_6;
  uStack_40a8 = 0;
  local_40b0 = 0;
  uStack_4098 = 0;
  uStack_40a0 = 0;
  iVar17 = 0xc;
  if (iVar15 == 8) {
    iVar17 = 0xd;
  }
  uStack_40c8 = 0;
  local_40d0 = 0;
  uStack_40b8 = 0;
  uStack_40c0 = 0;
  uStack_40e8 = 0;
  local_40f0 = 0;
  uStack_40d8 = 0;
  uStack_40e0 = 0;
  auVar13 = (undefined1  [8])param_3;
  if (param_5 == 0) {
joined_r0x0001b709d0e4:
    if (param_3 == 0) goto LAB_1b709d0ec;
  }
  else {
    uVar32 = param_5 - 4;
    if (3 < param_5) {
      puVar35 = param_4 + 1;
      uVar23 = *param_4;
      uVar24 = uVar23 & 0x800000ff;
      bVar9 = (uVar23 & 0x7f000000) != 0x61000000;
      if (bVar9) {
        uVar24 = 0xffffffff;
      }
      if ((!bVar9 && (int)uVar24 < 3) && (uVar24 & 0x7ffffffe) != 0) {
        if ((param_3 == 0) || (uVar32 == 0)) {
          if (param_3 == uVar32) goto LAB_1b709d0ec;
        }
        else if ((int)uVar23 < 0) {
          lVar21 = param_3 << (lVar11 == 0);
          if (param_5 == lVar21 + 4U) {
            if (lVar11 != 0) {
              lVar10 = lVar11;
            }
            func_0x0001b8120bb0(lVar10,puVar35,lVar21);
            goto LAB_1b709d0ec;
          }
        }
        else {
          if (uVar32 < 4) {
            lVar28 = 0;
          }
          else {
            local_4110 = (undefined1  [8])
                         (((ulong)param_4[1] << 0x20) >> ((ulong)(uint)-iVar15 & 0x3f));
            puVar33 = param_4 + 2;
            lVar36 = param_5 - 8;
            local_40f8 = (undefined1  [8])(param_6 & 0xffffffff);
            local_4100 = (undefined1  [8])(ulong)(0x40 - iVar15);
            uVar20 = ((ulong)param_4[1] << 0x20) << (param_6 & 0x3f);
            uVar24 = SUB84(local_4110,0) + 1;
            uVar29 = (ulong)uVar24;
            uVar38 = uVar20 >> 0x3d;
            iVar19 = 0x1d - iVar15;
            uVar30 = uVar20 << 3;
            local_4108 = (undefined1  [8])param_3;
            lVar28 = func_0x0001b8120b80(uVar29 << 3,0x100004000313f17);
            auVar13 = local_4110;
            iVar18 = 0;
            lVar21 = 0;
            uVar23 = (uint)(param_6 >> 1) & 0x7fffffff;
            uVar22 = uVar29;
            do {
              if (uVar38 == 0) {
                puVar34 = (uint *)(lVar28 + lVar21 * 8);
                lVar37 = lVar36;
                if (uVar24 == 2) {
                  *(undefined2 *)(puVar34 + 1) = 1;
                  if (iVar19 < 1) {
                    lVar37 = lVar36 + -4;
                    if (lVar36 < 4) {
                      uVar26 = 0;
                    }
                    else {
                      uVar26 = (ulong)*puVar33;
                      puVar33 = puVar33 + 1;
                    }
                    uVar30 = uVar26 << ((ulong)(0x20 - iVar19) & 0x3f) | uVar30;
                    iVar19 = iVar19 + 0x20;
                  }
                  iVar39 = iVar19 + -1;
                  uVar31 = uVar30 << 1;
                  *puVar34 = (uint)(uVar30 >> 0x3f);
                }
                else {
                  *puVar34 = 0;
                  *(undefined2 *)(puVar34 + 1) = 0;
                  uVar31 = uVar30;
                  iVar39 = iVar19;
                }
              }
              else {
                uVar4 = (uint)(uVar20 >> 0x20);
                lVar27 = lVar36;
                if (iVar19 < (int)(uVar4 >> 0x1d)) {
                  lVar27 = lVar36 + -4;
                  if (lVar36 < 4) {
                    uVar26 = 0;
                  }
                  else {
                    uVar26 = (ulong)*puVar33;
                    puVar33 = puVar33 + 1;
                  }
                  uVar30 = uVar26 << ((ulong)(0x20 - iVar19) & 0x3f) | uVar30;
                  iVar19 = iVar19 + 0x20;
                }
                iVar19 = iVar19 - (uVar4 >> 0x1d);
                uVar26 = uVar30 << uVar38;
                uVar4 = (int)(uVar30 >> (0x40 - uVar38 & 0x3f)) + 1;
                puVar1 = (undefined4 *)(lVar28 + lVar21 * 8);
                *(short *)(puVar1 + 1) = (short)uVar4;
                uVar4 = uVar4 & 0xffff;
                lVar37 = lVar27;
                if (iVar19 < (int)uVar4) {
                  lVar37 = lVar27 + -4;
                  if (lVar27 < 4) {
                    uVar30 = 0;
                  }
                  else {
                    uVar30 = (ulong)*puVar33;
                    puVar33 = puVar33 + 1;
                  }
                  uVar26 = uVar30 << ((ulong)(0x20 - iVar19) & 0x3f) | uVar26;
                  iVar19 = iVar19 + 0x20;
                }
                iVar39 = iVar19 - uVar4;
                uVar31 = uVar26 << ((ulong)uVar4 & 0x3f);
                *puVar1 = (int)(uVar26 >> ((ulong)-uVar4 & 0x3f));
              }
              lVar36 = lVar37;
              if (iVar39 < 1) {
                lVar36 = lVar37 + -4;
                if (lVar37 < 4) {
                  uVar30 = 0;
                }
                else {
                  uVar30 = (ulong)*puVar33;
                  puVar33 = puVar33 + 1;
                }
                uVar31 = uVar30 << ((ulong)(0x20 - iVar39) & 0x3f) | uVar31;
                iVar39 = iVar39 + 0x20;
              }
              iVar19 = iVar39 + -1;
              uVar30 = uVar31 << 1;
              if ((long)uVar31 < 0) {
                lVar27 = lVar36;
                if (iVar39 < 2) {
                  lVar27 = lVar36 + -4;
                  if (lVar36 < 4) {
                    uVar26 = 0;
                  }
                  else {
                    uVar26 = (ulong)*puVar33;
                    puVar33 = puVar33 + 1;
                  }
                  uVar30 = uVar26 << ((ulong)(0x21 - iVar39) & 0x3f) | uVar30;
                  iVar19 = iVar39 + 0x1f;
                }
                iVar39 = iVar19 + -1;
                uVar26 = uVar30 << 1;
                lVar36 = lVar27;
                if ((long)uVar30 < 0) {
                  if (iVar19 <= iVar15) {
                    lVar36 = lVar27 + -4;
                    if (lVar27 < 4) {
                      uVar30 = 0;
                    }
                    else {
                      uVar30 = (ulong)*puVar33;
                      puVar33 = puVar33 + 1;
                    }
                    uVar26 = uVar30 << ((ulong)(0x21 - iVar19) & 0x3f) | uVar26;
                    iVar39 = iVar19 + 0x1f;
                  }
                  iVar18 = (int)(uVar26 >> ((ulong)local_4100 & 0x3f));
                  iVar19 = iVar39 - iVar15;
                  uVar30 = uVar26 << ((ulong)local_40f8 & 0x3f);
                }
                else {
                  puVar34 = puVar33;
                  if (iVar19 <= (int)uVar23) {
                    lVar36 = lVar27 + -4;
                    if (lVar27 < 4) {
                      uVar30 = 0;
                    }
                    else {
                      puVar34 = puVar33 + 1;
                      uVar30 = (ulong)*puVar33;
                    }
                    uVar26 = uVar30 << ((ulong)(0x21 - iVar19) & 0x3f) | uVar26;
                    iVar39 = iVar19 + 0x1f;
                  }
                  iVar19 = iVar39 - uVar23;
                  uVar30 = uVar26 << (param_6 >> 1 & 0x3f);
                  iVar18 = iVar18 + (int)(uVar26 >> ((ulong)(0x40 - uVar23) & 0x3f));
                  puVar33 = puVar34;
                }
              }
              *(short *)(lVar28 + lVar21 * 8 + 6) = (short)iVar18;
              iVar18 = iVar18 + 1;
              lVar21 = lVar21 + 1;
              uVar22 = uVar22 - 1;
            } while (uVar22 != 0);
            if (-1 < lVar36) {
              puVar34 = (uint *)((long)puVar35 + ((long)puVar33 - (long)puVar35));
              uVar32 = uVar32 - ((long)puVar33 - (long)puVar35);
              if (-1 < (long)uVar32) {
                uVar22 = 0;
                uVar20 = 0;
                do {
                  iVar18 = (int)uVar20;
                  if (0 < iVar18) {
                    uVar30 = 0;
                    uVar5 = *(ushort *)(lVar28 + uVar22 * 8 + 4);
                    uVar24 = (uint)uVar5;
                    uVar38 = uVar20;
LAB_1b709d474:
                    uVar23 = *(uint *)((long)&local_40f0 + uVar30 * 4);
                    if (uVar23 != uVar5) {
                      if ((int)uVar23 < (int)(uint)uVar5) goto code_r0x0001b709d484;
                      uVar23 = (uint)uVar30;
                      if (iVar18 <= (int)uVar23) goto LAB_1b709d520;
                      uVar26 = uVar20 - uVar30;
                      if (uVar26 < 8) goto LAB_1b709d504;
                      lVar21 = 0;
                      uVar38 = uVar38 & 0xfffffffffffffff8;
                      do {
                        lVar27 = (uVar20 - lVar21) * 4;
                        uVar41 = *(undefined8 *)(local_4100 + lVar27);
                        uVar43 = *(undefined8 *)(local_4108 + lVar27);
                        uVar42 = *(undefined8 *)(local_4110 + lVar27);
                        lVar36 = (uVar20 - lVar21) * 4;
                        *(undefined8 *)(local_40f8 + lVar36 + 4) =
                             *(undefined8 *)(local_40f8 + lVar27);
                        *(undefined8 *)(local_4100 + lVar36 + 4) = uVar41;
                        *(undefined8 *)(local_4108 + lVar36 + 4) = uVar43;
                        *(undefined8 *)(local_4110 + lVar36 + 4) = uVar42;
                        lVar21 = lVar21 + 8;
                        uVar38 = uVar38 - 8;
                      } while (uVar38 != 0);
                      if (uVar26 != (uVar26 & 0xfffffffffffffff8)) {
                        uVar20 = uVar20 - (uVar26 & 0xfffffffffffffff8);
LAB_1b709d504:
                        do {
                          uVar38 = uVar20 - 1;
                          *(undefined4 *)((long)&local_40f0 + uVar20 * 4) =
                               *(undefined4 *)((long)&local_40f0 + uVar38 * 4);
                          uVar20 = uVar38;
                        } while ((long)(int)uVar23 < (long)uVar38);
                      }
LAB_1b709d520:
                      *(uint *)((long)&local_40f0 + uVar30 * 4) = uVar24;
                      uVar20 = (ulong)(iVar18 + 1U);
                      if (uVar23 == iVar18 + 1U) goto LAB_1b709d530;
                      goto LAB_1b709d44c;
                    }
                    goto LAB_1b709d49c;
                  }
                  uVar30 = 0;
LAB_1b709d49c:
                  if ((int)uVar30 == iVar18) {
LAB_1b709d530:
                    iVar18 = (int)uVar30;
                    uVar24 = (uint)*(ushort *)(lVar28 + uVar22 * 8 + 4);
LAB_1b709d444:
                    uVar20 = (ulong)(iVar18 + 1);
                    *(uint *)((long)&local_40f0 + (long)iVar18 * 4) = uVar24;
                  }
LAB_1b709d44c:
                  bVar9 = (undefined1  [8])uVar22 != auVar13;
                  uVar22 = uVar22 + 1;
                } while (bVar9);
                iVar19 = (int)uVar20;
                uVar22 = (long)iVar19 - 1;
                iVar18 = *(int *)((long)&local_40f0 + uVar22 * 4);
                if (iVar19 < 1) {
                  uVar24 = 0;
                  iVar39 = 0;
                  if (iVar19 != 0) {
                    iVar39 = iVar17;
                  }
                }
                else {
                  do {
                    iVar39 = *(int *)((long)&local_40f0 + (uVar22 & 0xffffffff) * 4);
                    if (iVar39 <= iVar17) goto LAB_1b709d570;
                    uVar24 = (int)uVar22 - 1;
                    uVar22 = (ulong)uVar24;
                  } while (uVar24 != 0xffffffff);
                  iVar39 = 0;
LAB_1b709d570:
                  lVar21 = 0;
                  uVar24 = 0;
                  do {
                    iVar17 = *(int *)((long)&local_40f0 + lVar21 * 4);
                    if (iVar39 < iVar17) {
                      *(int *)((long)&local_40f0 + (long)(int)uVar24 * 4) = iVar17;
                      uVar24 = uVar24 + 1;
                    }
                    lVar21 = lVar21 + 1;
                    uVar20 = uVar20 - 1;
                  } while (uVar20 != 0);
                }
                if (iVar15 == 8) {
                  func_0x0001b811fc60(local_4070,0x4000);
                  if (auVar13 == (undefined1  [8])0x0) {
                    if (0 < (long)local_4108) {
                      func_0x0001b8120bd0(lVar11,*(undefined1 *)(lVar28 + 6),local_4108);
                    }
                    goto LAB_1b709de84;
                  }
                  if (iVar39 < iVar18) {
                    uVar23 = 0x3fd;
                    lVar10 = func_0x0001b8120b70(0x3fd,8,0x100004000313f17);
                  }
                  else {
                    lVar10 = 0;
                    uVar23 = 0;
                  }
                  uVar22 = 0;
                  iVar17 = 0;
                  uVar4 = uVar23;
                  if (uVar23 < 2) {
                    uVar4 = 1;
                  }
                  do {
                    piVar2 = (int *)(lVar28 + uVar22 * 8);
                    uVar5 = *(ushort *)(piVar2 + 1);
                    uVar40 = iVar39 - (uint)uVar5;
                    if (iVar39 < (int)(uint)uVar5) {
                      uVar12 = *piVar2 << (ulong)(iVar18 - (uint)uVar5 & 0x1f);
                      uVar40 = (uVar12 ^ uVar12 >> 0x10) * -0x7a143595;
                      uVar40 = (uVar40 ^ uVar40 >> 0xd) * -0x3d4d51cb;
                      uVar40 = uVar40 ^ uVar40 >> 0x10;
                      uVar25 = uVar4;
                      do {
                        uVar16 = 0;
                        if (uVar23 != 0) {
                          uVar16 = uVar40 / uVar23;
                        }
                        uVar40 = uVar40 - uVar16 * uVar23;
                        if (*(int *)(lVar10 + (ulong)uVar40 * 8 + 4) == 0) {
                          iVar17 = iVar17 + 1;
                          puVar35 = (uint *)(lVar10 + (ulong)uVar40 * 8);
                          *puVar35 = uVar12;
                          puVar35[1] = (int)uVar22 + 1;
                          break;
                        }
                        uVar40 = uVar40 + 1;
                        uVar25 = uVar25 - 1;
                      } while (uVar25 != 0);
                    }
                    else {
                      uVar25 = *piVar2 << (ulong)(uVar40 & 0x1f);
                      uVar5 = *(ushort *)((long)piVar2 + 6) | uVar5 << 8;
                      *(ushort *)((long)local_4070 + (ulong)uVar25 * 2) = uVar5;
                      uVar12 = 1;
                      do {
                        *(ushort *)((long)local_4070 + (ulong)((uVar25 + uVar12) - 1) * 2) = uVar5;
                        uVar16 = uVar12 >> (ulong)(uVar40 & 0x1f);
                        uVar12 = uVar12 + 1;
                      } while (uVar16 == 0);
                    }
                    uVar22 = uVar22 + 1;
                  } while (uVar22 != uVar29);
                  if (iVar39 < iVar18) {
                    if (0 < (long)local_4108) {
                      local_4100._0_4_ = iVar17;
                      iVar17 = 0;
                      param_3 = 0;
                      uVar22 = 0;
                      uVar20 = uVar32;
LAB_1b709d7d4:
                      if (iVar39 < 1) {
LAB_1b709d824:
                        uVar32 = uVar20;
                        if (iVar17 < iVar18) {
                          uVar32 = uVar20 - 4;
                          if ((long)uVar20 < 4) {
                            uVar20 = 0;
                          }
                          else {
                            uVar20 = (ulong)*puVar34;
                            puVar34 = puVar34 + 1;
                          }
                          param_3 = uVar20 << ((ulong)(0x20 - iVar17) & 0x3f) | param_3;
                          iVar17 = iVar17 + 0x20;
                        }
                        uVar16 = (uint)(param_3 >> ((ulong)(0x40 - iVar18) & 0x3f));
                        uVar40 = (uVar16 ^ uVar16 >> 0x10) * -0x7a143595;
                        uVar12 = (uVar40 ^ uVar40 >> 0xd) * -0x3d4d51cb;
                        uVar12 = uVar12 ^ uVar12 >> 0x10;
                        uVar25 = uVar4;
                        uVar40 = uVar12;
                        do {
                          uVar7 = 0;
                          if (uVar23 != 0) {
                            uVar7 = uVar40 / uVar23;
                          }
                          uVar40 = uVar40 - uVar7 * uVar23;
                          puVar35 = (uint *)(lVar10 + (ulong)uVar40 * 8);
                          uVar7 = puVar35[1];
                          if (*puVar35 == uVar16) {
                            iVar15 = uVar7 - 1;
                            goto LAB_1b709d8a4;
                          }
                          if (uVar7 == 0) break;
                          uVar40 = uVar40 + 1;
                          uVar25 = uVar25 - 1;
                        } while (uVar25 != 0);
                        iVar15 = -1;
LAB_1b709d8a4:
                        if ((0 < (int)uVar24) && (iVar15 == -1)) {
                          local_40f8 = (undefined1  [8])uVar32;
                          uVar20 = 0;
                          do {
                            uVar7 = *(uint *)((long)&local_40f0 + uVar20 * 4);
                            uVar25 = -1 << (ulong)(iVar18 - uVar7 & 0x1f) & uVar16;
                            uVar40 = (uVar25 ^ uVar25 >> 0x10) * -0x7a143595;
                            uVar40 = (uVar40 ^ uVar40 >> 0xd) * -0x3d4d51cb;
                            uVar40 = uVar40 ^ uVar40 >> 0x10;
                            uVar14 = uVar23;
                            do {
                              uVar8 = 0;
                              if (uVar23 != 0) {
                                uVar8 = uVar40 / uVar23;
                              }
                              uVar40 = uVar40 - uVar8 * uVar23;
                              puVar35 = (uint *)(lVar10 + (ulong)uVar40 * 8);
                              uVar8 = puVar35[1];
                              if (*puVar35 == uVar25) {
                                if ((uVar8 != 0) &&
                                   (iVar15 = uVar8 - 1,
                                   uVar7 == *(ushort *)(lVar28 + (long)iVar15 * 8 + 4))) {
                                  uVar40 = uVar23;
                                  if (uVar23 <= (uint)(local_4100._0_4_ * 2)) goto LAB_1b709d7b0;
                                  goto LAB_1b709d958;
                                }
                                break;
                              }
                              if (uVar8 == 0) break;
                              uVar40 = uVar40 + 1;
                              uVar14 = uVar14 - 1;
                            } while (uVar14 != 0);
                            uVar20 = uVar20 + 1;
                          } while (uVar20 != uVar24);
                          iVar15 = -1;
                        }
                        goto LAB_1b709d7b0;
                      }
                      uVar32 = uVar20;
                      if (iVar17 < iVar39) {
                        uVar32 = uVar20 - 4;
                        if ((long)uVar20 < 4) {
                          uVar20 = 0;
                        }
                        else {
                          uVar20 = (ulong)*puVar34;
                          puVar34 = puVar34 + 1;
                        }
                        param_3 = uVar20 << ((ulong)(0x20 - iVar17) & 0x3f) | param_3;
                        iVar17 = iVar17 + 0x20;
                      }
                      uVar5 = *(ushort *)
                               ((long)local_4070 + (param_3 >> ((ulong)(0x40 - iVar39) & 0x3f)) * 2)
                      ;
                      uVar20 = uVar32;
                      if (uVar5 == 0) goto LAB_1b709d824;
                      *(char *)(lVar11 + uVar22) = (char)uVar5;
                      uVar5 = uVar5 >> 8;
                      goto LAB_1b709d7c0;
                    }
LAB_1b709ddf0:
                    param_3 = 0;
LAB_1b709ddf4:
                    func_0x0001b81206e0();
                  }
                  else {
                    if ((long)local_4108 < 1) goto LAB_1b709de84;
                    param_3 = 0;
                    iVar17 = 0;
                    lVar10 = 0;
                    auVar13 = local_4108;
                    uVar22 = uVar32;
                    do {
                      uVar32 = uVar22;
                      puVar35 = puVar34;
                      if (iVar17 < iVar39) {
                        uVar32 = uVar22 - 4;
                        if ((long)uVar22 < 4) {
                          uVar22 = 0;
                        }
                        else {
                          puVar35 = puVar34 + 1;
                          uVar22 = (ulong)*puVar34;
                        }
                        param_3 = uVar22 << ((ulong)(0x20 - iVar17) & 0x3f) | param_3;
                        iVar17 = iVar17 + 0x20;
                      }
                      uVar5 = *(ushort *)
                               ((long)local_4070 + (param_3 >> ((ulong)(0x40 - iVar39) & 0x3f)) * 2)
                      ;
                      *(char *)(lVar11 + lVar10) = (char)uVar5;
                      uVar5 = uVar5 >> 8;
                      iVar17 = iVar17 - (uint)uVar5;
                      param_3 = param_3 << ((ulong)uVar5 & 0x3f);
                      lVar10 = lVar10 + 1;
                      auVar13 = (undefined1  [8])((long)auVar13 - 1);
                      uVar22 = uVar32;
                      puVar34 = puVar35;
                    } while (auVar13 != (undefined1  [8])0x0);
                  }
                }
                else {
                  func_0x0001b811fc60(local_4070,0x4000);
                  if (auVar13 == (undefined1  [8])0x0) {
                    if (0 < (long)local_4108) {
                      uVar6 = *(undefined2 *)(lVar28 + 6);
                      if ((ulong)local_4108 < 4) {
                        uVar22 = 0;
                      }
                      else {
                        if ((ulong)local_4108 < 0x10) {
                          uVar20 = 0;
                        }
                        else {
                          lVar11 = 0;
                          uVar22 = (ulong)local_4108 & 0x7ffffffffffffff0;
                          uVar41 = CONCAT26(uVar6,CONCAT24(uVar6,CONCAT22(uVar6,uVar6)));
                          uVar42 = CONCAT26(uVar6,CONCAT24(uVar6,CONCAT22(uVar6,uVar6)));
                          uVar20 = uVar22;
                          do {
                            puVar3 = (undefined8 *)(lVar10 + lVar11 * 2);
                            puVar3[1] = uVar42;
                            *puVar3 = uVar41;
                            puVar3[3] = uVar42;
                            puVar3[2] = uVar41;
                            lVar11 = lVar11 + 0x10;
                            uVar20 = uVar20 - 0x10;
                          } while (uVar20 != 0);
                          if (local_4108 == (undefined1  [8])uVar22) goto LAB_1b709de84;
                          uVar20 = uVar22;
                          if (((ulong)local_4108 & 0xc) == 0) goto LAB_1b709de70;
                        }
                        uVar22 = (ulong)local_4108 & 0x7ffffffffffffffc;
                        lVar11 = uVar20 - uVar22;
                        do {
                          *(ulong *)(lVar10 + uVar20 * 2) =
                               CONCAT26(uVar6,CONCAT24(uVar6,CONCAT22(uVar6,uVar6)));
                          uVar20 = uVar20 + 4;
                          lVar11 = lVar11 + 4;
                        } while (lVar11 != 0);
                        if (local_4108 == (undefined1  [8])uVar22) goto LAB_1b709de84;
                      }
LAB_1b709de70:
                      lVar11 = (long)local_4108 - uVar22;
                      do {
                        *(undefined2 *)(lVar10 + uVar22 * 2) = uVar6;
                        uVar22 = uVar22 + 1;
                        lVar11 = lVar11 + -1;
                      } while (lVar11 != 0);
                    }
                  }
                  else {
                    if (iVar39 < iVar18) {
                      uVar23 = 0x1ffff;
                      lVar11 = func_0x0001b8120b70(0x1ffff,8,0x100004000313f17);
                    }
                    else {
                      lVar11 = 0;
                      uVar23 = 0;
                    }
                    uVar22 = 0;
                    iVar17 = 0;
                    uVar4 = uVar23;
                    if (uVar23 < 2) {
                      uVar4 = 1;
                    }
                    do {
                      piVar2 = (int *)(lVar28 + uVar22 * 8);
                      uVar5 = *(ushort *)(piVar2 + 1);
                      uVar40 = iVar39 - (uint)uVar5;
                      if (iVar39 < (int)(uint)uVar5) {
                        uVar12 = *piVar2 << (ulong)(iVar18 - (uint)uVar5 & 0x1f);
                        uVar40 = (uVar12 ^ uVar12 >> 0x10) * -0x7a143595;
                        uVar40 = (uVar40 ^ uVar40 >> 0xd) * -0x3d4d51cb;
                        uVar40 = uVar40 ^ uVar40 >> 0x10;
                        uVar25 = uVar4;
                        do {
                          uVar16 = 0;
                          if (uVar23 != 0) {
                            uVar16 = uVar40 / uVar23;
                          }
                          uVar40 = uVar40 - uVar16 * uVar23;
                          if (*(int *)(lVar11 + (ulong)uVar40 * 8 + 4) == 0) {
                            iVar17 = iVar17 + 1;
                            puVar35 = (uint *)(lVar11 + (ulong)uVar40 * 8);
                            *puVar35 = uVar12;
                            puVar35[1] = (int)uVar22 + 1;
                            break;
                          }
                          uVar40 = uVar40 + 1;
                          uVar25 = uVar25 - 1;
                        } while (uVar25 != 0);
                      }
                      else {
                        uVar25 = *piVar2 << (ulong)(uVar40 & 0x1f);
                        uVar16 = CONCAT22(uVar5,*(undefined2 *)((long)piVar2 + 6));
                        local_4070[uVar25] = uVar16;
                        uVar12 = 1;
                        do {
                          local_4070[(uVar25 + uVar12) - 1] = uVar16;
                          uVar7 = uVar12 >> (ulong)(uVar40 & 0x1f);
                          uVar12 = uVar12 + 1;
                        } while (uVar7 == 0);
                      }
                      uVar22 = uVar22 + 1;
                    } while (uVar22 != uVar29);
                    if (iVar39 < iVar18) {
                      if (0 < (long)local_4108) {
                        local_4100._0_4_ = iVar17;
                        iVar17 = 0;
                        param_3 = 0;
                        uVar22 = 0;
                        uVar20 = uVar32;
LAB_1b709dad8:
                        puVar35 = puVar34;
                        if (iVar39 < 1) {
LAB_1b709db3c:
                          uVar32 = uVar20;
                          if (iVar17 < iVar18) {
                            uVar32 = uVar20 - 4;
                            if ((long)uVar20 < 4) {
                              uVar20 = 0;
                            }
                            else {
                              uVar20 = (ulong)*puVar35;
                              puVar35 = puVar35 + 1;
                            }
                            param_3 = uVar20 << ((ulong)(0x20 - iVar17) & 0x3f) | param_3;
                            iVar17 = iVar17 + 0x20;
                          }
                          uVar16 = (uint)(param_3 >> ((ulong)(0x40 - iVar18) & 0x3f));
                          uVar40 = (uVar16 ^ uVar16 >> 0x10) * -0x7a143595;
                          uVar12 = (uVar40 ^ uVar40 >> 0xd) * -0x3d4d51cb;
                          uVar12 = uVar12 ^ uVar12 >> 0x10;
                          uVar25 = uVar4;
                          uVar40 = uVar12;
                          do {
                            uVar7 = 0;
                            if (uVar23 != 0) {
                              uVar7 = uVar40 / uVar23;
                            }
                            uVar40 = uVar40 - uVar7 * uVar23;
                            puVar33 = (uint *)(lVar11 + (ulong)uVar40 * 8);
                            uVar7 = puVar33[1];
                            if (*puVar33 == uVar16) {
                              iVar15 = uVar7 - 1;
                              goto LAB_1b709dbbc;
                            }
                            if (uVar7 == 0) break;
                            uVar40 = uVar40 + 1;
                            uVar25 = uVar25 - 1;
                          } while (uVar25 != 0);
                          iVar15 = -1;
LAB_1b709dbbc:
                          if ((0 < (int)uVar24) && (iVar15 == -1)) {
                            local_40f8 = (undefined1  [8])uVar32;
                            uVar20 = 0;
                            do {
                              uVar7 = *(uint *)((long)&local_40f0 + uVar20 * 4);
                              uVar25 = -1 << (ulong)(iVar18 - uVar7 & 0x1f) & uVar16;
                              uVar40 = (uVar25 ^ uVar25 >> 0x10) * -0x7a143595;
                              uVar40 = (uVar40 ^ uVar40 >> 0xd) * -0x3d4d51cb;
                              uVar40 = uVar40 ^ uVar40 >> 0x10;
                              uVar14 = uVar23;
                              do {
                                uVar8 = 0;
                                if (uVar23 != 0) {
                                  uVar8 = uVar40 / uVar23;
                                }
                                uVar40 = uVar40 - uVar8 * uVar23;
                                puVar33 = (uint *)(lVar11 + (ulong)uVar40 * 8);
                                uVar8 = puVar33[1];
                                if (*puVar33 == uVar25) {
                                  if ((uVar8 != 0) &&
                                     (iVar15 = uVar8 - 1,
                                     uVar7 == *(ushort *)(lVar28 + (long)iVar15 * 8 + 4))) {
                                    uVar40 = uVar23;
                                    if (uVar23 <= (uint)(local_4100._0_4_ * 2)) goto LAB_1b709dcb0;
                                    goto LAB_1b709dc70;
                                  }
                                  break;
                                }
                                if (uVar8 == 0) break;
                                uVar40 = uVar40 + 1;
                                uVar14 = uVar14 - 1;
                              } while (uVar14 != 0);
                              uVar20 = uVar20 + 1;
                            } while (uVar20 != uVar24);
                            iVar15 = -1;
                          }
                          goto LAB_1b709dcb0;
                        }
                        uVar32 = uVar20;
                        if (iVar17 < iVar39) {
                          uVar32 = uVar20 - 4;
                          if ((long)uVar20 < 4) {
                            uVar20 = 0;
                          }
                          else {
                            uVar20 = (ulong)*puVar34;
                            puVar34 = puVar34 + 1;
                          }
                          param_3 = uVar20 << ((ulong)(0x20 - iVar17) & 0x3f) | param_3;
                          iVar17 = iVar17 + 0x20;
                        }
                        uVar40 = local_4070[param_3 >> ((ulong)(0x40 - iVar39) & 0x3f)];
                        uVar20 = uVar32;
                        puVar35 = puVar34;
                        if (uVar40 == 0) goto LAB_1b709db3c;
                        *(short *)(lVar10 + uVar22 * 2) = (short)uVar40;
                        uVar20 = (ulong)(uVar40 >> 0x10);
                        if (iVar17 < (int)(uVar40 >> 0x10)) {
                          if ((long)uVar32 < 4) {
                            uVar29 = 0;
                          }
                          else {
                            uVar29 = (ulong)*puVar34;
                            puVar34 = puVar34 + 1;
                          }
                          param_3 = uVar29 << ((ulong)(0x20 - iVar17) & 0x3f) | param_3;
                          goto LAB_1b709dac0;
                        }
                        goto LAB_1b709dac4;
                      }
                      goto LAB_1b709ddf0;
                    }
                    if (0 < (long)local_4108) {
                      param_3 = 0;
                      iVar17 = 0;
                      lVar11 = 0;
                      auVar13 = local_4108;
                      uVar22 = uVar32;
                      do {
                        uVar32 = uVar22;
                        puVar35 = puVar34;
                        if (iVar17 < iVar39) {
                          uVar32 = uVar22 - 4;
                          if ((long)uVar22 < 4) {
                            uVar22 = 0;
                          }
                          else {
                            puVar35 = puVar34 + 1;
                            uVar22 = (ulong)*puVar34;
                          }
                          param_3 = uVar22 << ((ulong)(0x20 - iVar17) & 0x3f) | param_3;
                          iVar17 = iVar17 + 0x20;
                        }
                        uVar24 = local_4070[param_3 >> ((ulong)(0x40 - iVar39) & 0x3f)];
                        *(short *)(lVar10 + lVar11 * 2) = (short)uVar24;
                        uVar24 = uVar24 >> 0x10;
                        iVar17 = iVar17 - uVar24;
                        param_3 = param_3 << ((ulong)uVar24 & 0x3f);
                        lVar11 = lVar11 + 1;
                        auVar13 = (undefined1  [8])((long)auVar13 - 1);
                        uVar22 = uVar32;
                        puVar34 = puVar35;
                      } while (auVar13 != (undefined1  [8])0x0);
                      goto LAB_1b709de88;
                    }
                  }
LAB_1b709de84:
                  param_3 = 0;
                }
LAB_1b709de88:
                if (0xfffffffffffffffa < uVar32 - 1) {
                  if (uVar32 != 0xfffffffffffffffc) {
                    func_0x0001b81206e0(lVar28);
                    auVar13 = local_4108;
                    goto LAB_1b709d0ec;
                  }
                  func_0x0001b81206e0(lVar28);
                  auVar13 = local_4108;
                  goto joined_r0x0001b709d0e4;
                }
              }
            }
          }
          func_0x0001b81206e0(lVar28);
        }
      }
    }
  }
  auVar13 = (undefined1  [8])0xffffffffffffffff;
LAB_1b709d0ec:
  if (*_DAT_1e016af20 == local_70) {
    return (ulong)auVar13;
  }
  func_0x0001b811fac0();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
code_r0x0001b709d484:
  uVar30 = uVar30 + 1;
  uVar38 = uVar38 - 1;
  if (uVar20 == uVar30) goto LAB_1b709d444;
  goto LAB_1b709d474;
  while( true ) {
    uVar12 = uVar12 + 1;
    uVar40 = uVar40 - 1;
    if (uVar40 == 0) break;
LAB_1b709dc70:
    uVar25 = 0;
    if (uVar23 != 0) {
      uVar25 = uVar12 / uVar23;
    }
    uVar12 = uVar12 - uVar25 * uVar23;
    if (*(int *)(lVar11 + (ulong)uVar12 * 8 + 4) == 0) {
      local_4100._0_4_ = local_4100._0_4_ + 1;
      puVar33 = (uint *)(lVar11 + (ulong)uVar12 * 8);
      *puVar33 = uVar16;
      puVar33[1] = uVar8;
      break;
    }
  }
LAB_1b709dcb0:
  lVar21 = lVar28 + (long)iVar15 * 8;
  *(undefined2 *)(lVar10 + uVar22 * 2) = *(undefined2 *)(lVar21 + 6);
  uVar5 = *(ushort *)(lVar21 + 4);
  uVar20 = (ulong)uVar5;
  if (iVar17 < (int)(uint)uVar5) {
    if ((long)uVar32 < 4) {
      uVar29 = 0;
      puVar34 = puVar35;
    }
    else {
      puVar34 = puVar35 + 1;
      uVar29 = (ulong)*puVar35;
    }
    param_3 = uVar29 << ((ulong)(0x20 - iVar17) & 0x3f) | param_3;
LAB_1b709dac0:
    uVar32 = uVar32 - 4;
    iVar17 = iVar17 + 0x20;
    puVar35 = puVar34;
  }
LAB_1b709dac4:
  iVar17 = iVar17 - (int)uVar20;
  param_3 = param_3 << (uVar20 & 0x3f);
  uVar22 = uVar22 + 1;
  uVar20 = uVar32;
  puVar34 = puVar35;
  if ((undefined1  [8])uVar22 == local_4108) goto LAB_1b709ddf4;
  goto LAB_1b709dad8;
  while( true ) {
    uVar12 = uVar12 + 1;
    uVar40 = uVar40 - 1;
    if (uVar40 == 0) break;
LAB_1b709d958:
    uVar25 = 0;
    if (uVar23 != 0) {
      uVar25 = uVar12 / uVar23;
    }
    uVar12 = uVar12 - uVar25 * uVar23;
    if (*(int *)(lVar10 + (ulong)uVar12 * 8 + 4) == 0) {
      local_4100._0_4_ = local_4100._0_4_ + 1;
      puVar35 = (uint *)(lVar10 + (ulong)uVar12 * 8);
      *puVar35 = uVar16;
      puVar35[1] = uVar8;
      break;
    }
  }
LAB_1b709d7b0:
  lVar21 = lVar28 + (long)iVar15 * 8;
  *(undefined1 *)(lVar11 + uVar22) = *(undefined1 *)(lVar21 + 6);
  uVar5 = *(ushort *)(lVar21 + 4);
LAB_1b709d7c0:
  iVar17 = iVar17 - (uint)uVar5;
  param_3 = param_3 << ((ulong)uVar5 & 0x3f);
  uVar22 = uVar22 + 1;
  uVar20 = uVar32;
  if ((undefined1  [8])uVar22 == local_4108) goto LAB_1b709ddf4;
  goto LAB_1b709d7d4;
}

