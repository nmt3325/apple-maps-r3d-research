
undefined8
trico_mesh(float *param_1,ulong param_2,long *param_3,uint *param_4,long *param_5,uint *param_6,
          long *param_7,uint *param_8,long *param_9,long *param_10,long *param_11,long *param_12,
          uint *param_13,long *param_14,long *param_15)

{
  int *piVar1;
  uint uVar2;
  undefined8 *puVar3;
  undefined8 *puVar4;
  undefined8 *puVar5;
  undefined8 *puVar6;
  ulong *puVar7;
  undefined1 (*pauVar8) [12];
  char *pcVar9;
  undefined1 (*pauVar10) [16];
  uint uVar11;
  undefined4 uVar12;
  byte bVar13;
  byte bVar14;
  char cVar15;
  undefined1 auVar16 [16];
  undefined1 auVar17 [16];
  bool bVar18;
  bool bVar19;
  long lVar20;
  int *piVar21;
  undefined1 *puVar22;
  long lVar23;
  undefined1 *puVar24;
  uint *puVar25;
  long lVar26;
  long lVar27;
  undefined4 *puVar28;
  undefined8 uVar29;
  long lVar30;
  ulong uVar31;
  uint uVar32;
  uint uVar33;
  ulong uVar34;
  uint uVar35;
  uint uVar36;
  ulong uVar37;
  ulong uVar38;
  long lVar39;
  ulong uVar40;
  long lVar41;
  long lVar42;
  long lVar43;
  float *pfVar44;
  long lVar45;
  long lVar46;
  float *pfVar47;
  long lVar48;
  ulong uVar49;
  long *plVar50;
  float *pfVar51;
  undefined1 *puVar52;
  float *pfVar53;
  long lVar54;
  float fVar55;
  float fVar56;
  float extraout_s0;
  float fVar57;
  float fVar58;
  float fVar59;
  float fVar60;
  float fVar61;
  float fVar62;
  float fVar63;
  float fVar64;
  ulong uVar65;
  undefined1 auVar66 [16];
  undefined1 auVar67 [16];
  undefined1 auVar68 [16];
  undefined1 auVar69 [16];
  undefined1 auVar70 [16];
  undefined1 auVar71 [16];
  undefined4 extraout_var;
  float fVar72;
  undefined1 auVar74 [16];
  undefined1 auVar75 [16];
  undefined1 auVar76 [16];
  undefined1 auVar77 [16];
  undefined1 auVar78 [16];
  undefined1 auVar79 [16];
  undefined1 auVar80 [16];
  undefined1 auVar81 [16];
  undefined1 auVar82 [16];
  undefined1 auVar83 [16];
  float fVar73;
  undefined1 auVar84 [16];
  int iVar85;
  int iVar86;
  uint5 uVar87;
  undefined8 uVar88;
  undefined8 uVar89;
  int iVar98;
  undefined1 auVar90 [12];
  undefined1 auVar91 [12];
  undefined1 auVar92 [12];
  undefined1 auVar93 [12];
  undefined1 auVar94 [12];
  undefined1 auVar95 [12];
  undefined1 auVar96 [16];
  undefined1 auVar97 [16];
  int iVar99;
  int iVar100;
  int iVar101;
  int iVar102;
  int iVar103;
  int iVar104;
  undefined1 auVar105 [16];
  undefined1 auVar106 [16];
  undefined1 auVar107 [16];
  undefined1 auVar108 [16];
  long lStack_270;
  float *pfStack_268;
  uint uStack_238;
  ulong uStack_230;
  ulong uStack_1a0;
  float fStack_190;
  uint uStack_100;
  int iStack_fc;
  uint uStack_d8;
  undefined1 auStack_d4 [4];
  uint uStack_d0;
  undefined1 auStack_cc [4];
  uint uStack_c8;
  undefined1 auStack_c4 [4];
  uint uStack_c0;
  undefined1 auStack_bc [4];
  uint uStack_b8;
  undefined1 auStack_b4 [4];
  uint uStack_b0;
  undefined1 auStack_ac [4];
  uint uStack_a8;
  undefined1 auStack_a4 [4];
  uint uStack_a0;
  undefined1 auStack_9c [4];
  uint uStack_98;
  undefined1 auStack_94 [4];
  uint uStack_90;
  uint3 uStack_8c;
  
  *param_3 = 0;
  *param_5 = 0;
  *param_7 = 0;
  *param_11 = 0;
  *param_12 = 0;
  *param_10 = 0;
  *param_9 = 0;
  *param_8 = 0;
  *param_13 = 0;
  *param_6 = 0;
  uStack_100 = 0x80000000;
  *param_4 = 0;
  *param_14 = 0;
  uVar31 = param_2;
  pfVar51 = param_1;
  if (param_2 < 4) {
LAB_1b70975cc:
    fVar63 = 0.0;
    uVar33 = 0;
    uStack_100 = uStack_100 | 2;
  }
  else {
    uStack_100 = 0;
    if (*param_1 != 4.9901996e-17) {
      uStack_100 = 0x80000000;
    }
    uVar31 = param_2 - 4;
    pfVar51 = param_1 + 1;
    if (param_2 - 4 < 4) goto LAB_1b70975cc;
    pfVar51 = param_1 + 2;
    fVar63 = param_1[1];
    uVar31 = param_2 - 8;
    uVar33 = 0x80000000;
    if ((int)fVar63 < 4) {
      uVar33 = 0;
    }
  }
  fVar64 = 0.0;
  uStack_100 = uStack_100 | uVar33;
  if (uStack_100 == 0) {
    uVar65 = uVar31 - 4;
    if (uVar31 < 4) {
      uStack_100 = 2;
      goto LAB_1b709760c;
    }
    pfVar44 = pfVar51 + 1;
    fVar64 = *pfVar51;
    uVar31 = uVar31 - 8;
    if (3 < uVar65) {
      uStack_100 = 0;
      fVar72 = *pfVar44;
      pfVar44 = pfVar51 + 2;
      goto joined_r0x0001b7097650;
    }
LAB_1b7097638:
    lVar48 = 0;
    uStack_100 = 2;
    goto LAB_1b7099b68;
  }
LAB_1b709760c:
  fVar72 = 0.0;
  pfVar44 = pfVar51;
joined_r0x0001b7097650:
  if ((int)fVar63 < 3) {
    if (uStack_100 != 0) goto LAB_1b7097658;
    uVar65 = 0;
  }
  else {
    if (uStack_100 != 0) {
LAB_1b7097658:
      lVar48 = 0;
      goto LAB_1b7099b68;
    }
    bVar18 = uVar31 < 4;
    uVar31 = uVar31 - 4;
    if (bVar18) goto LAB_1b7097638;
    uVar65 = (ulong)(uint)*pfVar44;
    pfVar44 = pfVar44 + 1;
  }
  fVar55 = (float)uVar65;
  *param_15 = (long)pfVar44 - (long)param_1;
  pfVar51 = pfVar44;
  if (uVar31 == 0) {
LAB_1b709773c:
    uVar49 = 0;
    uStack_100 = 2;
  }
  else {
    bVar13 = *(byte *)pfVar44;
    uVar49 = uVar31 - 1;
    uVar34 = (ulong)bVar13 & 0x3f;
    bVar18 = (bVar13 & 0x40) == 0;
    uVar37 = 6;
    lVar48 = 0;
    pfVar53 = (float *)((long)pfVar44 + 1);
    uVar33 = 1;
    do {
      lVar20 = lVar48;
      lVar48 = uVar31 + lVar20;
      lVar45 = lVar48 + -1;
      if (bVar18) {
        uVar33 = -(uint)uVar34;
        if (-1 < (char)bVar13) {
          uVar33 = (uint)uVar34;
        }
        *param_13 = uVar33;
        if (lVar45 == 0) goto LAB_1b7097c44;
        pfVar44 = (float *)((long)pfVar53 + 1);
        bVar13 = *(byte *)pfVar53;
        uVar49 = lVar48 - 2;
        uVar34 = (ulong)bVar13 & 0x3f;
        bVar18 = (bVar13 & 0x40) == 0;
        pfVar53 = (float *)((long)pfVar53 + lVar45);
        uVar31 = 6;
        uVar37 = lVar48 - 4;
        uVar33 = 1;
        goto LAB_1b7097aa8;
      }
      pfVar51 = (float *)((long)pfVar44 + uVar31);
      if (lVar45 == 0) goto LAB_1b709773c;
      pfVar51 = (float *)((long)pfVar53 + 1);
      bVar14 = *(byte *)pfVar53;
      uVar49 = uVar49 - 1;
      if (((int)lVar20 == -8) && ((bVar14 & 0x7c) != 0)) goto LAB_1b709772c;
      bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
      uVar34 = ((ulong)bVar14 & 0x7f) << (uVar37 & 0x3f) | uVar34;
      uVar37 = uVar37 + 7;
      uVar35 = uVar33 + 1;
      bVar19 = uVar33 < 9;
      lVar48 = lVar20 + -1;
      pfVar53 = pfVar51;
      uVar33 = uVar35;
    } while ((bVar19) || (-1 < (char)bVar14));
    uVar49 = (uVar31 + lVar20) - 2;
LAB_1b709772c:
    uStack_100 = 0x10;
  }
  iVar101 = 0;
  *param_13 = 0;
  pfVar44 = pfVar51;
  uVar31 = 0;
  goto LAB_1b709775c;
  while( true ) {
    if (uVar40 == 0xfffffffffffffffe) goto LAB_1b7097c44;
    pfVar51 = (float *)((long)pfVar44 + 1);
    bVar14 = *(byte *)pfVar44;
    uVar49 = uVar49 - 1;
    pfVar44 = pfVar51;
    if ((uVar33 == 9) && ((bVar14 & 0x7c) != 0)) goto LAB_1b70999e8;
    bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
    uVar34 = ((ulong)bVar14 & 0x7f) << (uVar31 & 0x3f) | uVar34;
    uVar31 = uVar31 + 7;
    uVar35 = uVar33 + 1;
    bVar19 = 8 < uVar33;
    uVar37 = uVar40 - 1;
    uVar33 = uVar35;
    if ((bVar19) && ((char)bVar14 < 0)) break;
LAB_1b7097aa8:
    uVar40 = uVar37;
    if (bVar18) {
      iVar101 = -(int)uVar34;
      if (-1 < (char)bVar13) {
        iVar101 = (int)uVar34;
      }
      if (uVar40 + 2 != 0) {
        bVar13 = *(byte *)pfVar44;
        uVar49 = uVar40 + 1;
        uVar37 = (ulong)bVar13 & 0x3f;
        bVar18 = (bVar13 & 0x40) == 0;
        pfVar53 = (float *)((long)pfVar44 + uVar40 + 2);
        uVar31 = 6;
        pfVar44 = (float *)((long)pfVar44 + 1);
        uVar33 = 1;
        goto LAB_1b709995c;
      }
      uVar49 = 0;
      uStack_100 = 2;
      goto LAB_1b70999ec;
    }
  }
  uVar49 = uVar40 + 1;
LAB_1b70999e8:
  iVar101 = 0;
  uStack_100 = 0x10;
LAB_1b70999ec:
  uVar31 = 0;
  goto LAB_1b709775c;
  while( true ) {
    bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
    uVar37 = ((ulong)bVar14 & 0x7f) << (uVar31 & 0x3f) | uVar37;
    uVar31 = uVar31 + 7;
    uVar40 = uVar40 - 1;
    uVar49 = uVar49 - 1;
    uVar35 = uVar33 + 1;
    bVar19 = 8 < uVar33;
    uVar33 = uVar35;
    if ((bVar19) && ((char)bVar14 < 0)) break;
LAB_1b709995c:
    if (bVar18) {
      uStack_100 = 0;
      uVar49 = uVar40 + 1;
      uVar31 = -uVar37;
      if (-1 < (char)bVar13) {
        uVar31 = uVar37;
      }
      goto LAB_1b709775c;
    }
    if (uVar40 == 0xffffffffffffffff) goto LAB_1b7097c4c;
    pfVar51 = (float *)((long)pfVar44 + 1);
    bVar14 = *(byte *)pfVar44;
    pfVar44 = pfVar51;
    if ((uVar33 == 9) && ((bVar14 & 0x7c) != 0)) {
      uStack_100 = 0x10;
      uVar49 = uVar40;
      uVar31 = 0;
      goto LAB_1b709775c;
    }
  }
  uStack_100 = 0x10;
  uVar31 = 0;
LAB_1b709775c:
  lVar20 = func_0x0001b8120b80((long)iVar101,0x100004077774924);
  piVar21 = (int *)func_0x0001b8120b80(-(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 |
                                       (uVar31 & 0xffffffff) << 2,0x100004052888210);
  uVar35 = *param_13;
  uVar33 = uVar35 + 0xe;
  if (-8 < (int)uVar35) {
    uVar33 = uVar35 + 7;
  }
  lVar48 = (long)((ulong)uVar33 << 0x20) >> 0x23;
  if ((0xe < uVar35 + 0xe) && (uStack_100 == 0)) {
    auStack_d4._0_3_ = 0;
    uStack_d8 = 0;
    if (uVar49 == 0) {
      uVar37 = 0;
      pfVar51 = pfVar44;
LAB_1b7097870:
      auStack_d4._0_3_ = 0;
      uStack_100 = 2;
      uStack_d8 = 0;
      uVar49 = uVar37;
    }
    else {
      pfVar51 = (float *)((long)pfVar44 + 1);
      bVar13 = *(byte *)pfVar44;
      uVar37 = uVar49 - 1;
      if ((ulong)bVar13 == 0xff) {
        uVar34 = uVar49 - 9;
        if (uVar49 < 9) {
          uStack_100 = 2;
          uVar49 = uVar37;
          goto LAB_1b7097884;
        }
        uStack_d8 = *(uint *)((long)pfVar44 + 2);
        uVar49 = (ulong)*(byte *)((long)pfVar44 + 1);
        uVar37 = (ulong)*(uint7 *)((long)pfVar44 + 2);
        auStack_d4[2] = *(byte *)(pfVar44 + 2);
        auStack_d4._0_2_ = (short)*(undefined3 *)((long)pfVar44 + 6);
        pfVar51 = (float *)((long)pfVar44 + 9);
      }
      else {
        iVar86 = 7;
        if ((bVar13 & 0x40) != 0) {
          iVar86 = 8;
        }
        iVar85 = 6;
        if ((bVar13 & 0x20) != 0) {
          iVar85 = iVar86;
        }
        iVar86 = 5;
        if ((bVar13 & 0x10) != 0) {
          iVar86 = iVar85;
        }
        iVar85 = 4;
        if ((bVar13 & 8) != 0) {
          iVar85 = iVar86;
        }
        iVar86 = 3;
        if ((bVar13 & 4) != 0) {
          iVar86 = iVar85;
        }
        iVar85 = 2;
        if ((bVar13 & 2) != 0) {
          iVar85 = iVar86;
        }
        iVar86 = 1;
        if ((bVar13 & 1) != 0) {
          iVar86 = iVar85;
        }
        uVar49 = (ulong)(iVar86 - 1);
        uVar34 = uVar37 - uVar49;
        if (uVar37 < uVar49) goto LAB_1b7097870;
        func_0x0001b8120bb0(&uStack_d8,pfVar51,uVar49);
        pfVar51 = (float *)((long)pfVar51 + uVar49);
        uVar49 = ((ulong)uStack_d8 << 8 | (ulong)(uint3)auStack_d4._0_3_ << 0x28 | (ulong)bVar13) >>
                 iVar86;
        uVar37 = uVar49 >> 8;
        uStack_d8 = (uint)(uVar49 >> 8);
        auStack_d4._0_3_ = (undefined3)(uVar49 >> 0x28);
      }
      uVar37 = uVar49 & 0xff | uVar37 << 8;
      uVar49 = uVar34;
      if ((lVar20 == 0) || (lVar45 = byet(pfVar51,uVar37,lVar20,lVar48,1), lVar45 == lVar48)) {
        if (uVar34 < uVar37) {
          uStack_100 = 2;
        }
        else {
          uStack_100 = 0;
          pfVar51 = (float *)((long)pfVar51 + uVar37);
          uVar49 = uVar34 - uVar37;
        }
      }
      else {
        uStack_100 = 0x80000000;
      }
    }
LAB_1b7097884:
    uVar35 = *param_13;
    uVar33 = uVar35 + 0xe;
    if (-8 < (int)uVar35) {
      uVar33 = uVar35 + 7;
    }
    lVar48 = (long)((ulong)uVar33 << 0x20) >> 0x23;
    pfVar44 = pfVar51;
  }
  iVar101 = iVar101 - ((int)uVar33 >> 3);
  iVar86 = (int)uVar31;
  uVar37 = uVar49;
  if (iVar101 == 0 || uStack_100 != 0) {
LAB_1b70978bc:
    if (((uVar31 & 0xffffffff) != 0) && (uStack_100 == 0)) {
      auStack_c4._0_3_ = 0;
      uStack_c8 = 0;
      if (uVar37 == 0) {
        uVar34 = 0;
LAB_1b7097bc8:
        uVar37 = uVar34;
        auStack_c4._0_3_ = 0;
        uStack_100 = 2;
        uStack_c8 = 0;
      }
      else {
        pfVar51 = (float *)((long)pfVar44 + 1);
        bVar13 = *(byte *)pfVar44;
        uVar34 = uVar37 - 1;
        if ((ulong)bVar13 == 0xff) {
          bVar18 = uVar37 < 9;
          uVar37 = uVar37 - 9;
          if (bVar18) goto LAB_1b7097c70;
          uStack_c8 = *(uint *)((long)pfVar44 + 2);
          uVar34 = (ulong)*(byte *)((long)pfVar44 + 1);
          uVar49 = (ulong)*(uint7 *)((long)pfVar44 + 2);
          auStack_c4[2] = *(byte *)(pfVar44 + 2);
          auStack_c4._0_2_ = (short)*(undefined3 *)((long)pfVar44 + 6);
          pfVar44 = (float *)((long)pfVar44 + 9);
        }
        else {
          iVar101 = 7;
          if ((bVar13 & 0x40) != 0) {
            iVar101 = 8;
          }
          iVar85 = 6;
          if ((bVar13 & 0x20) != 0) {
            iVar85 = iVar101;
          }
          iVar101 = 5;
          if ((bVar13 & 0x10) != 0) {
            iVar101 = iVar85;
          }
          iVar85 = 4;
          if ((bVar13 & 8) != 0) {
            iVar85 = iVar101;
          }
          iVar101 = 3;
          if ((bVar13 & 4) != 0) {
            iVar101 = iVar85;
          }
          iVar85 = 2;
          if ((bVar13 & 2) != 0) {
            iVar85 = iVar101;
          }
          iVar101 = 1;
          if ((bVar13 & 1) != 0) {
            iVar101 = iVar85;
          }
          uVar49 = (ulong)(iVar101 - 1);
          uVar37 = uVar34 - uVar49;
          pfVar44 = pfVar51;
          if (uVar34 < uVar49) goto LAB_1b7097bc8;
          func_0x0001b8120bb0(&uStack_c8,pfVar51,uVar49);
          pfVar44 = (float *)((long)pfVar51 + uVar49);
          uVar34 = ((ulong)uStack_c8 << 8 | (ulong)(uint3)auStack_c4._0_3_ << 0x28 | (ulong)bVar13)
                   >> iVar101;
          uVar49 = uVar34 >> 8;
          uStack_c8 = (uint)(uVar34 >> 8);
          auStack_c4._0_3_ = (undefined3)(uVar34 >> 0x28);
        }
        uVar49 = uVar34 & 0xff | uVar49 << 8;
        if ((piVar21 == (int *)0x0) ||
           (lVar48 = byet(pfVar44,uVar49,piVar21,(long)iVar86,4), lVar48 == iVar86)) {
          if (uVar37 < uVar49) {
            uStack_100 = 2;
          }
          else {
            uStack_100 = 0;
            pfVar44 = (float *)((long)pfVar44 + uVar49);
            uVar37 = uVar37 - uVar49;
          }
        }
        else {
          uStack_100 = 0x80000000;
        }
      }
    }
  }
  else {
    auStack_cc._0_3_ = 0;
    uStack_d0 = 0;
    if (uVar49 == 0) {
      uVar34 = 0;
LAB_1b7097a50:
      auStack_cc._0_3_ = 0;
      uStack_d0 = 0;
      pfVar51 = pfVar44;
LAB_1b7097c70:
      pfVar44 = pfVar51;
      uVar37 = uVar34;
      uStack_100 = 2;
    }
    else {
      pfVar51 = (float *)((long)pfVar44 + 1);
      bVar13 = *(byte *)pfVar44;
      uVar34 = uVar49 - 1;
      if ((ulong)bVar13 == 0xff) {
        uVar37 = uVar49 - 9;
        if (uVar49 < 9) goto LAB_1b7097c70;
        uStack_d0 = *(uint *)((long)pfVar44 + 2);
        uVar34 = (ulong)*(byte *)((long)pfVar44 + 1);
        uVar49 = (ulong)*(uint7 *)((long)pfVar44 + 2);
        auStack_cc[2] = *(byte *)(pfVar44 + 2);
        auStack_cc._0_2_ = (short)*(undefined3 *)((long)pfVar44 + 6);
        pfVar44 = (float *)((long)pfVar44 + 9);
      }
      else {
        iVar85 = 7;
        if ((bVar13 & 0x40) != 0) {
          iVar85 = 8;
        }
        iVar98 = 6;
        if ((bVar13 & 0x20) != 0) {
          iVar98 = iVar85;
        }
        iVar85 = 5;
        if ((bVar13 & 0x10) != 0) {
          iVar85 = iVar98;
        }
        iVar98 = 4;
        if ((bVar13 & 8) != 0) {
          iVar98 = iVar85;
        }
        iVar85 = 3;
        if ((bVar13 & 4) != 0) {
          iVar85 = iVar98;
        }
        iVar98 = 2;
        if ((bVar13 & 2) != 0) {
          iVar98 = iVar85;
        }
        iVar85 = 1;
        if ((bVar13 & 1) != 0) {
          iVar85 = iVar98;
        }
        uVar49 = (ulong)(iVar85 - 1);
        uVar37 = uVar34 - uVar49;
        pfVar44 = pfVar51;
        if (uVar34 < uVar49) goto LAB_1b7097a50;
        func_0x0001b8120bb0(&uStack_d0,pfVar51,uVar49);
        pfVar44 = (float *)((long)pfVar51 + uVar49);
        uVar34 = ((ulong)uStack_d0 << 8 | (ulong)(uint3)auStack_cc._0_3_ << 0x28 | (ulong)bVar13) >>
                 iVar85;
        uVar49 = uVar34 >> 8;
        uStack_d0 = (uint)(uVar34 >> 8);
        auStack_cc._0_3_ = (undefined3)(uVar34 >> 0x28);
      }
      uVar49 = uVar34 & 0xff | uVar49 << 8;
      if ((lVar20 == 0) ||
         (lVar48 = byet(pfVar44,uVar49,lVar20 + lVar48,(long)iVar101,1), lVar48 == iVar101)) {
        if (uVar49 <= uVar37) {
          uStack_100 = 0;
          pfVar44 = (float *)((long)pfVar44 + uVar49);
          uVar37 = uVar37 - uVar49;
          goto LAB_1b70978bc;
        }
        uStack_100 = 2;
      }
      else {
        uStack_100 = 0x80000000;
      }
    }
  }
  uVar33 = *param_13;
  iVar101 = uVar33 + 0xe;
  if (-8 < (int)uVar33) {
    iVar101 = uVar33 + 7;
  }
  if (*piVar21 == 0x5a4c0000) {
    uVar33 = piVar21[1];
    *param_13 = uVar33;
    if ((int)uVar33 < 0) goto LAB_1b7098970;
    lVar48 = (ulong)uVar33 * 0xc;
    lVar45 = func_0x0001b8120b80(lVar48,0x100004052888210);
    puVar22 = (undefined1 *)func_0x0001b8120b80(lVar48,0x100004052888210);
    func_0x0001b8120bd0(lVar45,0xff,lVar48);
    func_0x0001b8120bd0(puVar22,0xff,lVar48);
    if (iVar86 < 6) {
      uVar49 = 2;
    }
    else {
      uVar49 = 2;
      do {
        uVar35 = piVar21[uVar49];
        uVar32 = *(uint *)((long)piVar21 + (uVar49 * 4 | 4));
        if (-1 < (int)uVar35) {
          *(uint *)(lVar45 + (ulong)uVar35 * 4) = uVar32;
        }
        if (-1 < (int)uVar32) {
          *(uint *)(lVar45 + (ulong)uVar32 * 4) = uVar35;
        }
        uVar49 = uVar49 + 2;
      } while ((long)uVar49 < (long)((uVar31 & 0x7fffffff) - 3));
    }
    bVar18 = false;
    lVar48 = 0;
    uVar31 = -(uVar49 >> 0x1f & 1) & 0xfffffffc00000000 | (uVar49 & 0xffffffff) << 2;
    uVar35 = *(uint *)((long)piVar21 + uVar31);
    *param_4 = uVar35;
    if (((int)uVar35 < 0) || (iVar86 = *(int *)((long)piVar21 + uVar31 + 4), iVar86 < 0)) {
      puVar52 = (undefined1 *)0x0;
      puVar24 = puVar22;
    }
    else {
      lVar23 = func_0x0001b8120b70((long)(int)*param_13,4,0x100004052888210);
      puVar24 = (undefined1 *)func_0x0001b8120b80((ulong)uVar33 * 3,0x100004077774924);
      uVar33 = *param_13;
      bVar18 = iVar86 == 0 && 0 < (int)uVar33;
      if (bVar18) {
        *puVar24 = 8;
        uVar33 = *param_13;
      }
      uVar31 = (ulong)bVar18;
      uVar35 = (uint)bVar18;
      if ((int)(uint)bVar18 < (int)uVar33) {
        uVar33 = 0;
        auVar68 = ZEXT816(0);
        iVar85 = 0;
        do {
          uVar35 = auVar68._0_4_;
          iVar100 = (int)uVar31;
          iVar98 = iVar85;
          if ((*(byte *)(lVar20 + ((int)uVar35 >> 3)) >> (ulong)(uVar35 & 7) & 1) == 0) {
            auVar68._0_4_ = uVar35 + 1;
            uVar31 = (ulong)(iVar100 + 1);
            puVar24[iVar100] = 0;
          }
          else {
            uVar32 = auVar68._4_4_;
            bVar13 = *(byte *)(lVar20 + (iVar101 >> 3) + (long)((int)uVar32 >> 2)) >>
                     (ulong)((uVar32 & 3) << 1) & 3 | 4;
            auVar68._0_4_ = uVar35 + 1;
            auVar68._4_4_ = uVar32 + 1;
            auVar68._8_8_ = 0;
            uVar31 = (long)iVar100 + 1;
            puVar24[iVar100] = bVar13;
            if (bVar13 == 7) {
              iVar98 = iVar85 + -1;
              if (iVar85 < 1) {
                uVar33 = uVar33 + 1;
                iVar98 = iVar85;
                if ((int)uVar31 < (int)*param_13) {
                  if ((int)uVar33 < iVar86) {
                    *(int *)(lVar23 + (long)(int)uVar33 * 4) = (int)uVar31;
                  }
                  else {
                    puVar24[uVar31] = 8;
                    uVar31 = (ulong)(iVar100 + 2);
                  }
                }
              }
            }
            else if ((bVar13 == 4) &&
                    (*(int *)(lVar45 + (long)((iVar100 * 3 + 2) % 3 + iVar100 * 3) * 4) == -1)) {
              iVar98 = iVar85 + 1;
            }
          }
          uVar35 = (uint)uVar31;
          iVar85 = iVar98;
        } while ((int)uVar35 < (int)*param_13);
      }
      else {
        uVar33 = 0;
      }
      uVar32 = *param_4;
      uVar31 = (ulong)(uVar35 - 1);
      if ((int)uVar35 < 1) {
        lVar48 = 0;
      }
      else {
        lVar48 = func_0x0001b8120b70(uVar35 * 3,4,0x100004052888210);
      }
      iVar101 = uVar32 - 1;
      if (0 < (int)uVar33) {
        uVar49 = 0;
        do {
          uVar33 = uVar33 - 1;
          uVar35 = 0xffffffff;
          for (uVar31 = (ulong)(int)uVar31;
              (iVar86 <= (int)uVar33 ||
              ((-1 < (int)uVar33 && ((long)*(int *)(lVar23 + (ulong)uVar33 * 4) <= (long)uVar31))));
              uVar31 = uVar31 - 1) {
            bVar13 = puVar24[uVar31];
            iVar85 = (int)uVar49;
            if (bVar13 < 6) {
              if (bVar13 == 0) {
                lVar42 = uVar31 * 3;
                if (-1 < (int)uVar35) {
                  *(int *)(lVar45 + (ulong)uVar35 * 4) = (int)(lVar42 + 1);
                }
                if (-1 < (long)uVar31) {
                  *(uint *)(lVar45 + (lVar42 + 1) * 4) = uVar35;
                }
                lVar46 = lVar42 + 2;
                iVar85 = (int)((ulong)(lVar46 * 0x55555556) >> 0x20);
                iVar100 = (iVar85 - (iVar85 >> 0x1f)) * 3;
                uVar35 = iVar100 + ((int)lVar42 + 4) % 3;
                piVar1 = (int *)(lVar45 + (long)(int)uVar35 * 4);
                iVar103 = (int)lVar46;
                iVar85 = *piVar1;
                lVar42 = lVar46;
                iVar98 = iVar103;
                while ((-1 < iVar85 && (iVar85 != iVar103))) {
                  *(int *)(puVar22 + (long)(((int)lVar42 + 1) % 3 + iVar100) * 4) = iVar101;
                  iVar98 = *piVar1;
                  lVar42 = (long)iVar98;
                  iVar100 = (iVar98 / 3) * 3;
                  uVar35 = iVar100 + (iVar98 + 2) % 3;
                  piVar1 = (int *)(lVar45 + (long)(int)uVar35 * 4);
                  iVar85 = *piVar1;
                }
                *(int *)(puVar22 + (long)((iVar98 + 1) % 3 + iVar100) * 4) = iVar101;
                if (-1 < (int)uVar35) {
                  *(int *)(lVar45 + (ulong)uVar35 * 4) = iVar103;
                }
                iVar101 = iVar101 + -1;
                if (-1 < (long)uVar31) {
                  *(uint *)(lVar45 + lVar46 * 4) = uVar35;
                }
              }
              else if (bVar13 == 4) {
                lVar42 = uVar31 * 3;
                if (-1 < (int)uVar35) {
                  *(int *)(lVar45 + (ulong)uVar35 * 4) = (int)(lVar42 + 1);
                }
                if ((long)uVar31 < 0) {
                  iVar98 = *(int *)(lVar45 + (lVar42 + 2) * 4);
                  if (iVar98 == -1 && lVar48 != 0) {
                    uVar49 = (long)iVar85 - 1;
                    uVar35 = *(uint *)(lVar48 + uVar49 * 4);
                    goto joined_r0x0001b7098784;
                  }
                  if (iVar98 < -1) {
                    uVar35 = -iVar98;
                    goto LAB_1b709857c;
                  }
                }
                else {
                  *(uint *)(lVar45 + (lVar42 + 1) * 4) = uVar35;
                  lVar46 = lVar42 + 2;
                  iVar98 = *(int *)(lVar45 + lVar46 * 4);
                  if (iVar98 == -1 && lVar48 != 0) {
                    uVar49 = (long)iVar85 - 1;
                    uVar35 = *(uint *)(lVar48 + uVar49 * 4);
                    *(uint *)(lVar45 + lVar46 * 4) = uVar35;
joined_r0x0001b7098784:
                    if (-1 < (int)uVar35) {
                      *(int *)(lVar45 + (ulong)uVar35 * 4) = (int)lVar42 + 2;
                    }
                  }
                  else if (iVar98 < -1) {
                    uVar35 = -iVar98;
                    *(uint *)(lVar45 + lVar46 * 4) = uVar35;
LAB_1b709857c:
                    uVar34 = lVar42 + 2;
                    *(int *)(lVar45 + (ulong)uVar35 * 4) = (int)uVar34;
                    do {
                      iVar85 = ((int)uVar34 / 3) * 3 + ((int)uVar34 + 1) % 3;
                      uVar35 = *(uint *)(lVar45 + (long)iVar85 * 4);
                      uVar34 = (ulong)uVar35;
                    } while (-1 < (int)uVar35);
                    iVar85 = (iVar85 / 3) * 3 + (iVar85 + 1) % 3;
                    do {
                      uVar35 = (iVar85 / 3) * 3 + (iVar85 + 1) % 3;
                      iVar85 = *(int *)(lVar45 + (long)(int)uVar35 * 4);
                    } while (-1 < iVar85);
                    do {
                      iVar85 = ((int)uVar35 / 3) * 3;
                      *(int *)(puVar22 + (long)(iVar85 + (int)(uVar35 + 1) % 3) * 4) = iVar101;
                      uVar35 = iVar85 + (int)(uVar35 + 2) % 3;
                      uVar32 = *(uint *)(lVar45 + (long)(int)uVar35 * 4);
                      while (-1 < (int)uVar32) {
                        iVar85 = (uVar32 / 3) * 3;
                        *(int *)(puVar22 + (ulong)(iVar85 + (uVar32 + 1) % 3) * 4) = iVar101;
                        uVar35 = iVar85 + (uVar32 + 2) % 3;
                        uVar32 = *(uint *)(lVar45 + (ulong)uVar35 * 4);
                      }
                      iVar101 = iVar101 + -1;
                    } while (*(int *)(puVar22 +
                                     (long)(((int)uVar35 / 3) * 3 + (int)(uVar35 + 1) % 3) * 4) ==
                             -1);
                  }
                }
              }
              else if (bVar13 == 5) {
                lVar42 = uVar31 * 3 + 2;
                goto joined_r0x0001b70982d0;
              }
            }
            else if (bVar13 == 6) {
              lVar42 = uVar31 * 3 + 1;
joined_r0x0001b70982d0:
              if (-1 < (int)uVar35) {
                *(int *)(lVar45 + (ulong)uVar35 * 4) = (int)lVar42;
              }
              if (-1 < (long)uVar31) {
                *(uint *)(lVar45 + lVar42 * 4) = uVar35;
              }
            }
            else if (bVar13 == 7) {
              if ((0 < (int)uVar35) && (lVar48 != 0)) {
                *(uint *)(lVar48 + (long)iVar85 * 4) = uVar35;
                uVar49 = (ulong)(iVar85 + 1);
              }
            }
            else if (bVar13 == 8) {
              uVar34 = uVar31 * 3;
              iVar85 = (int)uVar34;
              if (-1 < (int)uVar35) {
                *(int *)(lVar45 + (ulong)uVar35 * 4) = iVar85;
              }
              if (-1 < (long)uVar31) {
                *(uint *)(lVar45 + uVar31 * 0xc) = uVar35;
              }
              lVar42 = uVar34 + 1;
              iVar98 = (int)((ulong)(lVar42 * 0x55555556) >> 0x20);
              iVar103 = (iVar98 - (iVar98 >> 0x1f)) * 3;
              uVar35 = iVar103 + (iVar85 + 3) % 3;
              piVar1 = (int *)(lVar45 + (long)(int)uVar35 * 4);
              iVar99 = (int)lVar42;
              iVar98 = *piVar1;
              lVar46 = lVar42;
              iVar100 = iVar99;
              while ((-1 < iVar98 && (iVar98 != iVar99))) {
                *(int *)(puVar22 + (long)(((int)lVar46 + 1) % 3 + iVar103) * 4) = iVar101 + -2;
                iVar100 = *piVar1;
                lVar46 = (long)iVar100;
                iVar103 = (iVar100 / 3) * 3;
                uVar35 = iVar103 + (iVar100 + 2) % 3;
                piVar1 = (int *)(lVar45 + (long)(int)uVar35 * 4);
                iVar98 = *piVar1;
              }
              *(int *)(puVar22 + (long)((iVar100 + 1) % 3 + iVar103) * 4) = iVar101 + -2;
              if (-1 < (int)uVar35) {
                *(int *)(lVar45 + (ulong)uVar35 * 4) = iVar99;
              }
              if (-1 < (long)uVar31) {
                *(uint *)(lVar45 + lVar42 * 4) = uVar35;
              }
              lVar42 = uVar34 + 2;
              iVar98 = (int)((ulong)(lVar42 * 0x55555556) >> 0x20);
              iVar98 = iVar98 - (iVar98 >> 0x1f);
              iVar99 = iVar98 * 3;
              uVar35 = iVar99 + (iVar85 + 4) % 3;
              piVar1 = (int *)(lVar45 + (long)(int)uVar35 * 4);
              iVar102 = (int)lVar42;
              iVar100 = *piVar1;
              lVar46 = lVar42;
              iVar103 = iVar102;
              while ((-1 < iVar100 && (iVar100 != iVar102))) {
                *(int *)(puVar22 + (long)(((int)lVar46 + 1) % 3 + iVar99) * 4) = iVar101 + -1;
                iVar103 = *piVar1;
                lVar46 = (long)iVar103;
                iVar99 = (iVar103 / 3) * 3;
                uVar35 = iVar99 + (iVar103 + 2) % 3;
                piVar1 = (int *)(lVar45 + (long)(int)uVar35 * 4);
                iVar100 = *piVar1;
              }
              *(int *)(puVar22 + (long)((iVar103 + 1) % 3 + iVar99) * 4) = iVar101 + -1;
              if (-1 < (int)uVar35) {
                *(int *)(lVar45 + (ulong)uVar35 * 4) = iVar102;
              }
              if (-1 < (long)uVar31) {
                *(uint *)(lVar45 + lVar42 * 4) = uVar35;
              }
              uVar35 = iVar102 + iVar98 * -3 + iVar85;
              piVar1 = (int *)(lVar45 + (long)(int)uVar35 * 4);
              iVar98 = *piVar1;
              iVar100 = iVar85;
              uVar40 = uVar34;
              while ((-1 < iVar98 && (iVar98 != iVar85))) {
                *(int *)(puVar22 + (long)(((int)uVar34 + 1) % 3 + (int)uVar40) * 4) = iVar101;
                iVar100 = *piVar1;
                uVar34 = (ulong)iVar100;
                uVar35 = (iVar100 / 3) * 3;
                uVar40 = (ulong)uVar35;
                uVar35 = uVar35 + (iVar100 + 2) % 3;
                piVar1 = (int *)(lVar45 + (long)(int)uVar35 * 4);
                iVar98 = *piVar1;
              }
              *(int *)(puVar22 + (long)((iVar100 + 1) % 3 + (int)uVar40) * 4) = iVar101;
              if (-1 < (int)uVar35) {
                *(int *)(lVar45 + (ulong)uVar35 * 4) = iVar85;
              }
              if (-1 < (long)uVar31) {
                *(uint *)(lVar45 + uVar31 * 0xc) = uVar35;
              }
              iVar101 = iVar101 + -3;
              uVar33 = uVar33 - 1;
            }
            uVar35 = (int)uVar31 * 3;
          }
          if (iVar86 != 0) {
            iVar85 = *(int *)(lVar23 + (long)(int)uVar33 * 4) * 3;
            iVar85 = ((iVar85 + 1) / 3) * 3 + (iVar85 + 2) % 3;
            do {
              uVar35 = (iVar85 / 3) * 3 + (iVar85 + 1) % 3;
              iVar85 = *(int *)(lVar45 + (long)(int)uVar35 * 4);
            } while (-1 < iVar85);
            do {
              iVar85 = ((int)uVar35 / 3) * 3;
              *(int *)(puVar22 + (long)(iVar85 + (int)(uVar35 + 1) % 3) * 4) = iVar101;
              uVar35 = iVar85 + (int)(uVar35 + 2) % 3;
              uVar32 = *(uint *)(lVar45 + (long)(int)uVar35 * 4);
              while (-1 < (int)uVar32) {
                iVar85 = (uVar32 / 3) * 3;
                *(int *)(puVar22 + (ulong)(iVar85 + (uVar32 + 1) % 3) * 4) = iVar101;
                uVar35 = iVar85 + (uVar32 + 2) % 3;
                uVar32 = *(uint *)(lVar45 + (ulong)uVar35 * 4);
              }
              iVar101 = iVar101 + -1;
            } while (*(int *)(puVar22 + (long)(((int)uVar35 / 3) * 3 + (int)(uVar35 + 1) % 3) * 4)
                     == -1);
            iVar86 = iVar86 + -1;
          }
        } while (0 < (int)uVar33);
      }
      func_0x0001b81206e0();
      if (iVar101 == -1) {
        bVar18 = true;
        lVar48 = lVar45;
        lVar45 = lVar23;
        puVar52 = puVar22;
      }
      else {
        func_0x0001b81206e0(lVar45);
        func_0x0001b81206e0(puVar22);
        bVar18 = false;
        lVar48 = 0;
        lVar45 = lVar23;
        puVar52 = (undefined1 *)0x0;
      }
    }
    func_0x0001b81206e0(lVar45);
    func_0x0001b81206e0(puVar24);
    if (!bVar18) goto LAB_1b7098970;
    *param_9 = (long)puVar52;
  }
  else {
LAB_1b7098970:
    lVar48 = 0;
    uStack_100 = uStack_100 | 0x80000000;
  }
  func_0x0001b81206e0(lVar20);
  func_0x0001b81206e0(piVar21);
  *param_15 = (long)((long)pfVar44 + (-*param_15 - (long)param_1));
  if (uStack_100 != 0) goto LAB_1b7099b68;
  lVar20 = func_0x0001b8120b80((long)(int)*param_4 * 0xc,0x10000403e1c8ba9);
  *param_3 = lVar20;
  param_15[1] = (long)pfVar44 - (long)param_1;
  uVar33 = *param_4;
  lVar42 = *param_9;
  uVar35 = *param_13;
  lVar23 = (long)(int)uVar35;
  lVar45 = func_0x0001b8120b80((long)(int)uVar33 * 0xc,0x10000403e1c8ba9);
  if (uVar33 == 0) {
    uStack_100 = 0;
  }
  else {
    auStack_bc._0_3_ = 0;
    uStack_c0 = 0;
    if (uVar37 == 0) {
      uVar31 = 0;
      pfVar51 = pfVar44;
LAB_1b7098ab0:
      auStack_bc._0_3_ = 0;
      uStack_100 = 2;
      uStack_c0 = 0;
      pfVar44 = pfVar51;
      uVar37 = uVar31;
    }
    else {
      pfVar51 = (float *)((long)pfVar44 + 1);
      bVar13 = *(byte *)pfVar44;
      uVar31 = uVar37 - 1;
      if ((ulong)bVar13 == 0xff) {
        uVar49 = uVar37 - 9;
        if (uVar37 < 9) {
          uStack_100 = 2;
          pfVar44 = pfVar51;
          uVar37 = uVar31;
          goto LAB_1b7098ac8;
        }
        uStack_c0 = *(uint *)((long)pfVar44 + 2);
        uVar37 = (ulong)*(byte *)((long)pfVar44 + 1);
        uVar31 = (ulong)*(uint7 *)((long)pfVar44 + 2);
        auStack_bc[2] = *(byte *)(pfVar44 + 2);
        auStack_bc._0_2_ = (short)*(undefined3 *)((long)pfVar44 + 6);
        pfVar44 = (float *)((long)pfVar44 + 9);
      }
      else {
        iVar101 = 7;
        if ((bVar13 & 0x40) != 0) {
          iVar101 = 8;
        }
        iVar86 = 6;
        if ((bVar13 & 0x20) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 5;
        if ((bVar13 & 0x10) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 4;
        if ((bVar13 & 8) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 3;
        if ((bVar13 & 4) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 2;
        if ((bVar13 & 2) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 1;
        if ((bVar13 & 1) != 0) {
          iVar101 = iVar86;
        }
        uVar37 = (ulong)(iVar101 - 1);
        uVar49 = uVar31 - uVar37;
        if (uVar31 < uVar37) goto LAB_1b7098ab0;
        func_0x0001b8120bb0(&uStack_c0,pfVar51,uVar37);
        pfVar44 = (float *)((long)pfVar51 + uVar37);
        uVar37 = ((ulong)uStack_c0 << 8 | (ulong)(uint3)auStack_bc._0_3_ << 0x28 | (ulong)bVar13) >>
                 iVar101;
        uVar31 = uVar37 >> 8;
        uStack_c0 = (uint)(uVar37 >> 8);
        auStack_bc._0_3_ = (undefined3)(uVar37 >> 0x28);
      }
      uVar31 = uVar37 & 0xff | uVar31 << 8;
      uVar37 = uVar49;
      if ((lVar45 == 0) ||
         (lVar46 = byet(pfVar44,uVar31,lVar45,(long)(int)uVar33,0xc), lVar46 == (int)uVar33)) {
        if (uVar49 < uVar31) {
          uStack_100 = 2;
        }
        else {
          uStack_100 = 0;
          pfVar44 = (float *)((long)pfVar44 + uVar31);
          uVar37 = uVar49 - uVar31;
        }
      }
      else {
        uStack_100 = 0x80000000;
      }
    }
  }
LAB_1b7098ac8:
  puVar25 = (uint *)func_0x0001b8120b80(lVar23 << 2,0x100004052888210);
  if (fVar63 == 0.0) {
    lVar26 = func_0x0001b8120b70(lVar23,1,0xd3a49843);
    lVar27 = func_0x0001b8120b70((long)(int)uVar33,1,0xc3244059);
    iVar101 = 0;
    lVar46 = 0;
    uVar29 = 0;
    fVar56 = 0.0;
    while( true ) {
      if ((int)lVar46 < (int)uVar35) {
        lVar46 = (long)(int)lVar46;
        while (*(char *)(lVar26 + lVar46) != '\0') {
          lVar46 = lVar46 + 1;
          if (lVar23 == lVar46) goto LAB_1b7099550;
        }
      }
      uVar33 = (uint)lVar46;
      if (uVar33 == uVar35) break;
      lVar54 = (long)(int)uVar33 + (long)(int)uVar33 * 2;
      lVar41 = (long)(int)lVar54 * 4;
      lVar30 = (long)*(int *)(lVar42 + lVar41);
      lVar39 = (long)*(int *)(lVar42 + lVar54 * 4 + 4);
      lVar54 = (long)*(int *)(lVar42 + lVar41 + 8);
      if (*(char *)(lVar27 + lVar30) == '\0') {
        puVar3 = (undefined8 *)(lVar20 + lVar30 * 0xc);
        pauVar8 = (undefined1 (*) [12])(lVar45 + lVar30 * 0xc);
        uVar88 = *(undefined8 *)*pauVar8;
        iVar100 = (int)uVar88 >> 1;
        iVar103 = (int)((long)uVar88 >> 0x21);
        iVar99 = *(int *)(*pauVar8 + 8) >> 1;
        uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar88 & 1)) & 0x100ffffff;
        iVar86 = -(int)uVar87;
        iVar85 = -(uint)(byte)(uVar87 >> 0x20);
        iVar98 = -(uint)(SUB121(*pauVar8,8) & 1);
        auVar78[0] = (byte)iVar100 ^ (byte)iVar86;
        auVar78[1] = (byte)((uint)iVar100 >> 8) ^ (byte)((uint)iVar86 >> 8);
        auVar78[2] = (byte)((uint)iVar100 >> 0x10) ^ (byte)((uint)iVar86 >> 0x10);
        auVar78[3] = (char)((ulong)uVar88 >> 0x18) >> 1 ^ (byte)((uint)iVar86 >> 0x18);
        auVar78[4] = (byte)iVar103 ^ (byte)iVar85;
        auVar78[5] = (byte)((uint)iVar103 >> 8) ^ (byte)((uint)iVar85 >> 8);
        auVar78[6] = (byte)((uint)iVar103 >> 0x10) ^ (byte)((uint)iVar85 >> 0x10);
        auVar78[7] = (byte)((long)uVar88 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18);
        auVar78[8] = (byte)iVar99 ^ (byte)iVar98;
        auVar78[9] = (byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8);
        auVar78[10] = (byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10);
        auVar78[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar98 >> 0x18);
        auVar78._12_4_ = 0;
        auVar68 = NEON_scvtf(auVar78,4);
        *(float *)(puVar3 + 1) = fVar56 + auVar68._8_4_ * fVar64;
        *puVar3 = CONCAT44((float)((ulong)uVar29 >> 0x20) + auVar68._4_4_ * fVar64,
                           (float)uVar29 + auVar68._0_4_ * fVar64);
        *(undefined1 *)(lVar27 + lVar30) = 1;
        if (*(char *)(lVar27 + lVar39) == '\0') goto LAB_1b70993dc;
LAB_1b70990a0:
        cVar15 = *(char *)(lVar27 + lVar54);
      }
      else {
        if (*(char *)(lVar27 + lVar39) != '\0') goto LAB_1b70990a0;
LAB_1b70993dc:
        puVar3 = (undefined8 *)(lVar20 + lVar30 * 0xc);
        uVar29 = *puVar3;
        fVar56 = *(float *)(puVar3 + 1);
        puVar3 = (undefined8 *)(lVar20 + lVar39 * 0xc);
        pauVar8 = (undefined1 (*) [12])(lVar45 + lVar39 * 0xc);
        uVar88 = *(undefined8 *)*pauVar8;
        iVar100 = (int)uVar88 >> 1;
        iVar103 = (int)((long)uVar88 >> 0x21);
        iVar99 = *(int *)(*pauVar8 + 8) >> 1;
        uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar88 & 1)) & 0x100ffffff;
        iVar86 = -(int)uVar87;
        iVar85 = -(uint)(byte)(uVar87 >> 0x20);
        iVar98 = -(uint)(SUB121(*pauVar8,8) & 1);
        auVar96[0] = (byte)iVar100 ^ (byte)iVar86;
        auVar96[1] = (byte)((uint)iVar100 >> 8) ^ (byte)((uint)iVar86 >> 8);
        auVar96[2] = (byte)((uint)iVar100 >> 0x10) ^ (byte)((uint)iVar86 >> 0x10);
        auVar96[3] = (char)((ulong)uVar88 >> 0x18) >> 1 ^ (byte)((uint)iVar86 >> 0x18);
        auVar96[4] = (byte)iVar103 ^ (byte)iVar85;
        auVar96[5] = (byte)((uint)iVar103 >> 8) ^ (byte)((uint)iVar85 >> 8);
        auVar96[6] = (byte)((uint)iVar103 >> 0x10) ^ (byte)((uint)iVar85 >> 0x10);
        auVar96[7] = (byte)((long)uVar88 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18);
        auVar96[8] = (byte)iVar99 ^ (byte)iVar98;
        auVar96[9] = (byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8);
        auVar96[10] = (byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10);
        auVar96[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar98 >> 0x18);
        auVar96._12_4_ = 0;
        auVar68 = NEON_scvtf(auVar96,4);
        *(float *)(puVar3 + 1) = fVar56 + auVar68._8_4_ * fVar64;
        *puVar3 = CONCAT44((float)((ulong)uVar29 >> 0x20) + auVar68._4_4_ * fVar64,
                           (float)uVar29 + auVar68._0_4_ * fVar64);
        *(undefined1 *)(lVar27 + lVar39) = 1;
        cVar15 = *(char *)(lVar27 + lVar54);
      }
      if (cVar15 == '\0') {
        puVar3 = (undefined8 *)(lVar20 + lVar39 * 0xc);
        puVar4 = (undefined8 *)(lVar20 + lVar30 * 0xc);
        uVar29 = *puVar3;
        uVar88 = *puVar4;
        fVar57 = ((float)uVar88 + (float)uVar29) * SUB164(ZEXT816(0x3f0000003f000000),0);
        fVar58 = ((float)((ulong)uVar88 >> 0x20) + (float)((ulong)uVar29 >> 0x20)) *
                 SUB164(ZEXT816(0x3f0000003f000000),4);
        uVar29 = CONCAT44(fVar58,fVar57);
        fVar56 = (*(float *)(puVar4 + 1) + *(float *)(puVar3 + 1)) * 0.5;
        puVar3 = (undefined8 *)(lVar20 + lVar54 * 0xc);
        pauVar8 = (undefined1 (*) [12])(lVar45 + lVar54 * 0xc);
        uVar88 = *(undefined8 *)*pauVar8;
        iVar100 = (int)uVar88 >> 1;
        iVar103 = (int)((long)uVar88 >> 0x21);
        iVar99 = *(int *)(*pauVar8 + 8) >> 1;
        uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar88 & 1)) & 0x100ffffff;
        iVar86 = -(int)uVar87;
        iVar85 = -(uint)(byte)(uVar87 >> 0x20);
        iVar98 = -(uint)(SUB121(*pauVar8,8) & 1);
        auVar108[0] = (byte)iVar100 ^ (byte)iVar86;
        auVar108[1] = (byte)((uint)iVar100 >> 8) ^ (byte)((uint)iVar86 >> 8);
        auVar108[2] = (byte)((uint)iVar100 >> 0x10) ^ (byte)((uint)iVar86 >> 0x10);
        auVar108[3] = (char)((ulong)uVar88 >> 0x18) >> 1 ^ (byte)((uint)iVar86 >> 0x18);
        auVar108[4] = (byte)iVar103 ^ (byte)iVar85;
        auVar108[5] = (byte)((uint)iVar103 >> 8) ^ (byte)((uint)iVar85 >> 8);
        auVar108[6] = (byte)((uint)iVar103 >> 0x10) ^ (byte)((uint)iVar85 >> 0x10);
        auVar108[7] = (byte)((long)uVar88 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18);
        auVar108[8] = (byte)iVar99 ^ (byte)iVar98;
        auVar108[9] = (byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8);
        auVar108[10] = (byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10);
        auVar108[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar98 >> 0x18);
        auVar108._12_4_ = 0;
        auVar68 = NEON_scvtf(auVar108,4);
        *(float *)(puVar3 + 1) = fVar56 + auVar68._8_4_ * fVar64;
        *puVar3 = CONCAT44(fVar58 + auVar68._4_4_ * fVar64,fVar57 + auVar68._0_4_ * fVar64);
        *(undefined1 *)(lVar27 + lVar54) = 1;
      }
      lVar54 = 0;
      puVar25[iVar101] = uVar33;
      iVar101 = 1;
      *(undefined1 *)(lVar26 + (int)uVar33) = 1;
      do {
        lVar30 = (long)(int)puVar25[lVar54];
        uVar31 = lVar30 * 3;
        iVar86 = *(int *)(lVar48 + lVar30 * 0xc);
        if (iVar86 != -1) {
          lVar39 = (long)*(int *)(lVar42 + (long)iVar86 * 4);
          if (*(char *)(lVar27 + lVar39) == '\0') {
            uVar49 = -(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 | (uVar31 & 0xffffffff) << 2;
            puVar3 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + uVar49 + 4) * 0xc);
            puVar4 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + uVar49 + 8) * 0xc);
            puVar5 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + lVar30 * 0xc) * 0xc);
            uVar29 = *puVar3;
            uVar88 = *puVar4;
            uVar89 = *puVar5;
            fVar57 = ((float)uVar88 + (float)uVar29) - (float)uVar89;
            fVar58 = ((float)((ulong)uVar88 >> 0x20) + (float)((ulong)uVar29 >> 0x20)) -
                     (float)((ulong)uVar89 >> 0x20);
            uVar29 = CONCAT44(fVar58,fVar57);
            fVar56 = (*(float *)(puVar4 + 1) + *(float *)(puVar3 + 1)) - *(float *)(puVar5 + 1);
            puVar3 = (undefined8 *)(lVar20 + lVar39 * 0xc);
            pauVar8 = (undefined1 (*) [12])(lVar45 + lVar39 * 0xc);
            uVar88 = *(undefined8 *)*pauVar8;
            iVar103 = (int)uVar88 >> 1;
            iVar99 = (int)((long)uVar88 >> 0x21);
            iVar102 = *(int *)(*pauVar8 + 8) >> 1;
            uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar88 & 1)) & 0x1ffffffff;
            iVar85 = -(int)uVar87;
            iVar98 = -(uint)(byte)(uVar87 >> 0x20);
            iVar100 = -(uint)(SUB121(*pauVar8,8) & 1);
            auVar105[0] = (byte)iVar103 ^ (byte)iVar85;
            auVar105[1] = (byte)((uint)iVar103 >> 8) ^ (byte)((uint)iVar85 >> 8);
            auVar105[2] = (byte)((uint)iVar103 >> 0x10) ^ (byte)((uint)iVar85 >> 0x10);
            auVar105[3] = (char)((ulong)uVar88 >> 0x18) >> 1 ^ (byte)((uint)iVar85 >> 0x18);
            auVar105[4] = (byte)iVar99 ^ (byte)iVar98;
            auVar105[5] = (byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8);
            auVar105[6] = (byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10);
            auVar105[7] = (byte)((long)uVar88 >> 0x39) ^ (byte)((uint)iVar98 >> 0x18);
            auVar105[8] = (byte)iVar102 ^ (byte)iVar100;
            auVar105[9] = (byte)((uint)iVar102 >> 8) ^ (byte)((uint)iVar100 >> 8);
            auVar105[10] = (byte)((uint)iVar102 >> 0x10) ^ (byte)((uint)iVar100 >> 0x10);
            auVar105[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar100 >> 0x18);
            auVar105._12_4_ = 0;
            auVar68 = NEON_scvtf(auVar105,4);
            *(float *)(puVar3 + 1) = fVar56 + auVar68._8_4_ * fVar64;
            *puVar3 = CONCAT44(fVar58 + auVar68._4_4_ * fVar64,fVar57 + auVar68._0_4_ * fVar64);
            *(undefined1 *)(lVar27 + lVar39) = 1;
          }
          uVar33 = iVar86 / 3;
          if (*(char *)(lVar26 + (int)uVar33) == '\0') {
            puVar25[iVar101] = uVar33;
            iVar101 = iVar101 + 1;
            *(undefined1 *)(lVar26 + (int)uVar33) = 1;
          }
        }
        iVar86 = *(int *)(lVar48 + (uVar31 + 1) * 4);
        if (iVar86 != -1) {
          lVar39 = (long)*(int *)(lVar42 + (long)iVar86 * 4);
          if (*(char *)(lVar27 + lVar39) == '\0') {
            puVar3 = (undefined8 *)
                     (lVar20 + (long)*(int *)(lVar42 + (-(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 |
                                                       (uVar31 & 0xffffffff) << 2) + 8) * 0xc);
            puVar4 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + lVar30 * 0xc) * 0xc);
            puVar5 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + (uVar31 + 1) * 4) * 0xc);
            uVar29 = *puVar3;
            uVar88 = *puVar4;
            uVar89 = *puVar5;
            fVar57 = ((float)uVar88 + (float)uVar29) - (float)uVar89;
            fVar58 = ((float)((ulong)uVar88 >> 0x20) + (float)((ulong)uVar29 >> 0x20)) -
                     (float)((ulong)uVar89 >> 0x20);
            uVar29 = CONCAT44(fVar58,fVar57);
            fVar56 = (*(float *)(puVar4 + 1) + *(float *)(puVar3 + 1)) - *(float *)(puVar5 + 1);
            puVar3 = (undefined8 *)(lVar20 + lVar39 * 0xc);
            pauVar8 = (undefined1 (*) [12])(lVar45 + lVar39 * 0xc);
            uVar88 = *(undefined8 *)*pauVar8;
            iVar103 = (int)uVar88 >> 1;
            iVar99 = (int)((long)uVar88 >> 0x21);
            iVar102 = *(int *)(*pauVar8 + 8) >> 1;
            uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar88 & 1)) & 0x100ffffff;
            iVar85 = -(int)uVar87;
            iVar98 = -(uint)(byte)(uVar87 >> 0x20);
            iVar100 = -(uint)(SUB121(*pauVar8,8) & 1);
            auVar106[0] = (byte)iVar103 ^ (byte)iVar85;
            auVar106[1] = (byte)((uint)iVar103 >> 8) ^ (byte)((uint)iVar85 >> 8);
            auVar106[2] = (byte)((uint)iVar103 >> 0x10) ^ (byte)((uint)iVar85 >> 0x10);
            auVar106[3] = (char)((ulong)uVar88 >> 0x18) >> 1 ^ (byte)((uint)iVar85 >> 0x18);
            auVar106[4] = (byte)iVar99 ^ (byte)iVar98;
            auVar106[5] = (byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8);
            auVar106[6] = (byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10);
            auVar106[7] = (byte)((long)uVar88 >> 0x39) ^ (byte)((uint)iVar98 >> 0x18);
            auVar106[8] = (byte)iVar102 ^ (byte)iVar100;
            auVar106[9] = (byte)((uint)iVar102 >> 8) ^ (byte)((uint)iVar100 >> 8);
            auVar106[10] = (byte)((uint)iVar102 >> 0x10) ^ (byte)((uint)iVar100 >> 0x10);
            auVar106[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar100 >> 0x18);
            auVar106._12_4_ = 0;
            auVar68 = NEON_scvtf(auVar106,4);
            *(float *)(puVar3 + 1) = fVar56 + auVar68._8_4_ * fVar64;
            *puVar3 = CONCAT44(fVar58 + auVar68._4_4_ * fVar64,fVar57 + auVar68._0_4_ * fVar64);
            *(undefined1 *)(lVar27 + lVar39) = 1;
          }
          uVar33 = iVar86 / 3;
          if (*(char *)(lVar26 + (int)uVar33) == '\0') {
            puVar25[iVar101] = uVar33;
            iVar101 = iVar101 + 1;
            *(undefined1 *)(lVar26 + (int)uVar33) = 1;
          }
        }
        iVar86 = *(int *)(lVar48 + (uVar31 + 2) * 4);
        if (iVar86 != -1) {
          lVar39 = (long)*(int *)(lVar42 + (long)iVar86 * 4);
          if (*(char *)(lVar27 + lVar39) == '\0') {
            puVar3 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + lVar30 * 0xc) * 0xc);
            puVar4 = (undefined8 *)
                     (lVar20 + (long)*(int *)(lVar42 + (-(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 |
                                                       (uVar31 & 0xffffffff) << 2) + 4) * 0xc);
            puVar5 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + (uVar31 + 2) * 4) * 0xc);
            uVar29 = *puVar3;
            uVar88 = *puVar4;
            uVar89 = *puVar5;
            fVar57 = ((float)uVar88 + (float)uVar29) - (float)uVar89;
            fVar58 = ((float)((ulong)uVar88 >> 0x20) + (float)((ulong)uVar29 >> 0x20)) -
                     (float)((ulong)uVar89 >> 0x20);
            uVar29 = CONCAT44(fVar58,fVar57);
            fVar56 = (*(float *)(puVar4 + 1) + *(float *)(puVar3 + 1)) - *(float *)(puVar5 + 1);
            puVar3 = (undefined8 *)(lVar20 + lVar39 * 0xc);
            pauVar8 = (undefined1 (*) [12])(lVar45 + lVar39 * 0xc);
            uVar88 = *(undefined8 *)*pauVar8;
            iVar103 = (int)uVar88 >> 1;
            iVar99 = (int)((long)uVar88 >> 0x21);
            iVar102 = *(int *)(*pauVar8 + 8) >> 1;
            uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar88 & 1)) & 0x100ffffff;
            iVar85 = -(int)uVar87;
            iVar98 = -(uint)(byte)(uVar87 >> 0x20);
            iVar100 = -(uint)(SUB121(*pauVar8,8) & 1);
            auVar107[0] = (byte)iVar103 ^ (byte)iVar85;
            auVar107[1] = (byte)((uint)iVar103 >> 8) ^ (byte)((uint)iVar85 >> 8);
            auVar107[2] = (byte)((uint)iVar103 >> 0x10) ^ (byte)((uint)iVar85 >> 0x10);
            auVar107[3] = (char)((ulong)uVar88 >> 0x18) >> 1 ^ (byte)((uint)iVar85 >> 0x18);
            auVar107[4] = (byte)iVar99 ^ (byte)iVar98;
            auVar107[5] = (byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8);
            auVar107[6] = (byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10);
            auVar107[7] = (byte)((long)uVar88 >> 0x39) ^ (byte)((uint)iVar98 >> 0x18);
            auVar107[8] = (byte)iVar102 ^ (byte)iVar100;
            auVar107[9] = (byte)((uint)iVar102 >> 8) ^ (byte)((uint)iVar100 >> 8);
            auVar107[10] = (byte)((uint)iVar102 >> 0x10) ^ (byte)((uint)iVar100 >> 0x10);
            auVar107[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar100 >> 0x18);
            auVar107._12_4_ = 0;
            auVar68 = NEON_scvtf(auVar107,4);
            *(float *)(puVar3 + 1) = fVar56 + auVar68._8_4_ * fVar64;
            *puVar3 = CONCAT44(fVar58 + auVar68._4_4_ * fVar64,fVar57 + auVar68._0_4_ * fVar64);
            *(undefined1 *)(lVar27 + lVar39) = 1;
          }
          uVar33 = iVar86 / 3;
          if (*(char *)(lVar26 + (int)uVar33) == '\0') {
            puVar25[iVar101] = uVar33;
            iVar101 = iVar101 + 1;
            *(undefined1 *)(lVar26 + (int)uVar33) = 1;
          }
        }
        lVar54 = lVar54 + 1;
      } while (lVar54 < iVar101);
    }
  }
  else {
    lVar26 = func_0x0001b8120b70(lVar23,1,0x97281173);
    lVar27 = func_0x0001b8120b70((long)(int)uVar33,1,0x82b1e991);
    iVar101 = 0;
    lVar46 = 0;
    auVar74 = ZEXT816(0);
    while( true ) {
      if ((int)lVar46 < (int)uVar35) {
        lVar46 = (long)(int)lVar46;
        while (*(char *)(lVar26 + lVar46) != '\0') {
          lVar46 = lVar46 + 1;
          if (lVar23 == lVar46) goto LAB_1b7098fb4;
        }
      }
      uVar32 = (uint)lVar46;
      if (uVar32 == uVar35) break;
      lVar54 = (long)(int)uVar32 + (long)(int)uVar32 * 2;
      lVar41 = (long)(int)lVar54 * 4;
      lVar30 = (long)*(int *)(lVar42 + lVar41);
      lVar39 = (long)*(int *)(lVar42 + lVar54 * 4 + 4);
      lVar54 = (long)*(int *)(lVar42 + lVar41 + 8);
      if (*(char *)(lVar27 + lVar30) == '\0') {
        puVar3 = (undefined8 *)(lVar20 + lVar30 * 0xc);
        pauVar8 = (undefined1 (*) [12])(lVar45 + lVar30 * 0xc);
        uVar29 = *(undefined8 *)*pauVar8;
        iVar100 = (int)uVar29 >> 1;
        iVar103 = (int)((long)uVar29 >> 0x21);
        iVar99 = *(int *)(*pauVar8 + 8) >> 1;
        uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar29 & 1)) & 0x100ffffff;
        iVar86 = -(int)uVar87;
        iVar85 = -(uint)(byte)(uVar87 >> 0x20);
        iVar98 = -(uint)(SUB121(*pauVar8,8) & 1);
        iVar86 = CONCAT13((char)((ulong)uVar29 >> 0x18) >> 1 ^ (byte)((uint)iVar86 >> 0x18),
                          CONCAT12((byte)((uint)iVar100 >> 0x10) ^ (byte)((uint)iVar86 >> 0x10),
                                   CONCAT11((byte)((uint)iVar100 >> 8) ^ (byte)((uint)iVar86 >> 8),
                                            (byte)iVar100 ^ (byte)iVar86)));
        auVar93._0_8_ =
             CONCAT17((byte)((long)uVar29 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18),
                      CONCAT16((byte)((uint)iVar103 >> 0x10) ^ (byte)((uint)iVar85 >> 0x10),
                               CONCAT15((byte)((uint)iVar103 >> 8) ^ (byte)((uint)iVar85 >> 8),
                                        CONCAT14((byte)iVar103 ^ (byte)iVar85,iVar86))));
        auVar93[8] = (byte)iVar99 ^ (byte)iVar98;
        auVar93[9] = (byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8);
        auVar93[10] = (byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10);
        auVar93[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar98 >> 0x18);
        *puVar3 = CONCAT44((int)((ulong)auVar93._0_8_ >> 0x20) + auVar74._4_4_,
                           iVar86 + auVar74._0_4_);
        *(int *)(puVar3 + 1) = auVar93._8_4_ + iVar101;
        *(undefined1 *)(lVar27 + lVar30) = 1;
        if (*(char *)(lVar27 + lVar39) == '\0') goto LAB_1b7098ed0;
LAB_1b7098ba4:
        cVar15 = *(char *)(lVar27 + lVar54);
      }
      else {
        if (*(char *)(lVar27 + lVar39) != '\0') goto LAB_1b7098ba4;
LAB_1b7098ed0:
        puVar7 = (ulong *)(lVar20 + lVar30 * 0xc);
        auVar74._0_8_ = *puVar7;
        auVar74._8_8_ = 0;
        iVar101 = (int)puVar7[1];
        puVar3 = (undefined8 *)(lVar20 + lVar39 * 0xc);
        pauVar8 = (undefined1 (*) [12])(lVar45 + lVar39 * 0xc);
        uVar29 = *(undefined8 *)*pauVar8;
        iVar100 = (int)uVar29 >> 1;
        iVar103 = (int)((long)uVar29 >> 0x21);
        iVar99 = *(int *)(*pauVar8 + 8) >> 1;
        uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar29 & 1)) & 0x100ffffff;
        iVar86 = -(int)uVar87;
        iVar85 = -(uint)(byte)(uVar87 >> 0x20);
        iVar98 = -(uint)(SUB121(*pauVar8,8) & 1);
        iVar86 = CONCAT13((char)((ulong)uVar29 >> 0x18) >> 1 ^ (byte)((uint)iVar86 >> 0x18),
                          CONCAT12((byte)((uint)iVar100 >> 0x10) ^ (byte)((uint)iVar86 >> 0x10),
                                   CONCAT11((byte)((uint)iVar100 >> 8) ^ (byte)((uint)iVar86 >> 8),
                                            (byte)iVar100 ^ (byte)iVar86)));
        auVar94._0_8_ =
             CONCAT17((byte)((long)uVar29 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18),
                      CONCAT16((byte)((uint)iVar103 >> 0x10) ^ (byte)((uint)iVar85 >> 0x10),
                               CONCAT15((byte)((uint)iVar103 >> 8) ^ (byte)((uint)iVar85 >> 8),
                                        CONCAT14((byte)iVar103 ^ (byte)iVar85,iVar86))));
        auVar94[8] = (byte)iVar99 ^ (byte)iVar98;
        auVar94[9] = (byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8);
        auVar94[10] = (byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10);
        auVar94[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar98 >> 0x18);
        *puVar3 = CONCAT44((int)((ulong)auVar94._0_8_ >> 0x20) + (int)(auVar74._0_8_ >> 0x20),
                           iVar86 + (int)auVar74._0_8_);
        *(int *)(puVar3 + 1) = auVar94._8_4_ + iVar101;
        *(undefined1 *)(lVar27 + lVar39) = 1;
        cVar15 = *(char *)(lVar27 + lVar54);
      }
      if (cVar15 == '\0') {
        puVar3 = (undefined8 *)(lVar20 + lVar30 * 0xc);
        puVar4 = (undefined8 *)(lVar20 + lVar39 * 0xc);
        uVar29 = *puVar3;
        uVar88 = *puVar4;
        iVar101 = CONCAT13(~(byte)((ulong)uVar29 >> 0x18),
                           CONCAT12(~(byte)((ulong)uVar29 >> 0x10),
                                    CONCAT11(~(byte)((ulong)uVar29 >> 8),~(byte)uVar29)));
        auVar74._0_4_ = ((int)uVar88 - iVar101) / 2;
        auVar74._4_4_ =
             ((int)((ulong)uVar88 >> 0x20) -
             (int)(CONCAT17(~(byte)((ulong)uVar29 >> 0x38),
                            CONCAT16(~(byte)((ulong)uVar29 >> 0x30),
                                     CONCAT15(~(byte)((ulong)uVar29 >> 0x28),
                                              CONCAT14(~(byte)((ulong)uVar29 >> 0x20),iVar101)))) >>
                  0x20)) / 2;
        auVar74._8_8_ = 0;
        puVar5 = (undefined8 *)(lVar20 + lVar54 * 0xc);
        pauVar8 = (undefined1 (*) [12])(lVar45 + lVar54 * 0xc);
        iVar101 = (*(int *)(puVar3 + 1) + *(int *)(puVar4 + 1) + 1) / 2;
        uVar29 = *(undefined8 *)*pauVar8;
        iVar100 = (int)uVar29 >> 1;
        iVar103 = (int)((long)uVar29 >> 0x21);
        iVar99 = *(int *)(*pauVar8 + 8) >> 1;
        uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar29 & 1)) & 0x100ffffff;
        iVar86 = -(int)uVar87;
        iVar85 = -(uint)(byte)(uVar87 >> 0x20);
        iVar98 = -(uint)(SUB121(*pauVar8,8) & 1);
        iVar86 = CONCAT13((char)((ulong)uVar29 >> 0x18) >> 1 ^ (byte)((uint)iVar86 >> 0x18),
                          CONCAT12((byte)((uint)iVar100 >> 0x10) ^ (byte)((uint)iVar86 >> 0x10),
                                   CONCAT11((byte)((uint)iVar100 >> 8) ^ (byte)((uint)iVar86 >> 8),
                                            (byte)iVar100 ^ (byte)iVar86)));
        auVar95._0_8_ =
             CONCAT17((byte)((long)uVar29 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18),
                      CONCAT16((byte)((uint)iVar103 >> 0x10) ^ (byte)((uint)iVar85 >> 0x10),
                               CONCAT15((byte)((uint)iVar103 >> 8) ^ (byte)((uint)iVar85 >> 8),
                                        CONCAT14((byte)iVar103 ^ (byte)iVar85,iVar86))));
        auVar95[8] = (byte)iVar99 ^ (byte)iVar98;
        auVar95[9] = (byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8);
        auVar95[10] = (byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10);
        auVar95[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar98 >> 0x18);
        *puVar5 = CONCAT44((int)((ulong)auVar95._0_8_ >> 0x20) + auVar74._4_4_,
                           iVar86 + auVar74._0_4_);
        *(int *)(puVar5 + 1) = auVar95._8_4_ + iVar101;
        *(undefined1 *)(lVar27 + lVar54) = 1;
      }
      lVar54 = 0;
      *puVar25 = uVar32;
      iVar86 = 1;
      *(undefined1 *)(lVar26 + (int)uVar32) = 1;
      do {
        lVar30 = (long)(int)puVar25[lVar54];
        uVar31 = lVar30 * 3;
        iVar85 = *(int *)(lVar48 + lVar30 * 0xc);
        if (iVar85 != -1) {
          lVar39 = (long)*(int *)(lVar42 + (long)iVar85 * 4);
          if (*(char *)(lVar27 + lVar39) == '\0') {
            uVar49 = -(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 | (uVar31 & 0xffffffff) << 2;
            puVar3 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + uVar49 + 4) * 0xc);
            puVar4 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + uVar49 + 8) * 0xc);
            puVar5 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + lVar30 * 0xc) * 0xc);
            uVar29 = *puVar3;
            uVar88 = *puVar4;
            uVar89 = *puVar5;
            auVar74._0_4_ = ((int)uVar88 + (int)uVar29) - (int)uVar89;
            auVar74._4_4_ =
                 ((int)((ulong)uVar88 >> 0x20) + (int)((ulong)uVar29 >> 0x20)) -
                 (int)((ulong)uVar89 >> 0x20);
            auVar74._8_8_ = 0;
            puVar6 = (undefined8 *)(lVar20 + lVar39 * 0xc);
            pauVar8 = (undefined1 (*) [12])(lVar45 + lVar39 * 0xc);
            iVar101 = (*(int *)(puVar4 + 1) + *(int *)(puVar3 + 1)) - *(int *)(puVar5 + 1);
            uVar29 = *(undefined8 *)*pauVar8;
            iVar99 = (int)uVar29 >> 1;
            iVar102 = (int)((long)uVar29 >> 0x21);
            iVar104 = *(int *)(*pauVar8 + 8) >> 1;
            uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar29 & 1)) & 0x1ffffffff;
            iVar98 = -(int)uVar87;
            iVar100 = -(uint)(byte)(uVar87 >> 0x20);
            iVar103 = -(uint)(SUB121(*pauVar8,8) & 1);
            iVar98 = CONCAT13((char)((ulong)uVar29 >> 0x18) >> 1 ^ (byte)((uint)iVar98 >> 0x18),
                              CONCAT12((byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10),
                                       CONCAT11((byte)((uint)iVar99 >> 8) ^
                                                (byte)((uint)iVar98 >> 8),
                                                (byte)iVar99 ^ (byte)iVar98)));
            auVar90._0_8_ =
                 CONCAT17((byte)((long)uVar29 >> 0x39) ^ (byte)((uint)iVar100 >> 0x18),
                          CONCAT16((byte)((uint)iVar102 >> 0x10) ^ (byte)((uint)iVar100 >> 0x10),
                                   CONCAT15((byte)((uint)iVar102 >> 8) ^ (byte)((uint)iVar100 >> 8),
                                            CONCAT14((byte)iVar102 ^ (byte)iVar100,iVar98))));
            auVar90[8] = (byte)iVar104 ^ (byte)iVar103;
            auVar90[9] = (byte)((uint)iVar104 >> 8) ^ (byte)((uint)iVar103 >> 8);
            auVar90[10] = (byte)((uint)iVar104 >> 0x10) ^ (byte)((uint)iVar103 >> 0x10);
            auVar90[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar103 >> 0x18);
            *puVar6 = CONCAT44((int)((ulong)auVar90._0_8_ >> 0x20) + auVar74._4_4_,
                               iVar98 + auVar74._0_4_);
            *(int *)(puVar6 + 1) = auVar90._8_4_ + iVar101;
            *(undefined1 *)(lVar27 + lVar39) = 1;
          }
          uVar32 = iVar85 / 3;
          if (*(char *)(lVar26 + (int)uVar32) == '\0') {
            puVar25[iVar86] = uVar32;
            iVar86 = iVar86 + 1;
            *(undefined1 *)(lVar26 + (int)uVar32) = 1;
          }
        }
        iVar85 = *(int *)(lVar48 + (uVar31 + 1) * 4);
        if (iVar85 != -1) {
          lVar39 = (long)*(int *)(lVar42 + (long)iVar85 * 4);
          if (*(char *)(lVar27 + lVar39) == '\0') {
            puVar3 = (undefined8 *)
                     (lVar20 + (long)*(int *)(lVar42 + (-(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 |
                                                       (uVar31 & 0xffffffff) << 2) + 8) * 0xc);
            puVar4 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + lVar30 * 0xc) * 0xc);
            puVar5 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + (uVar31 + 1) * 4) * 0xc);
            uVar29 = *puVar3;
            uVar88 = *puVar4;
            uVar89 = *puVar5;
            auVar74._0_4_ = ((int)uVar88 + (int)uVar29) - (int)uVar89;
            auVar74._4_4_ =
                 ((int)((ulong)uVar88 >> 0x20) + (int)((ulong)uVar29 >> 0x20)) -
                 (int)((ulong)uVar89 >> 0x20);
            auVar74._8_8_ = 0;
            puVar6 = (undefined8 *)(lVar20 + lVar39 * 0xc);
            pauVar8 = (undefined1 (*) [12])(lVar45 + lVar39 * 0xc);
            iVar101 = (*(int *)(puVar4 + 1) + *(int *)(puVar3 + 1)) - *(int *)(puVar5 + 1);
            uVar29 = *(undefined8 *)*pauVar8;
            iVar99 = (int)uVar29 >> 1;
            iVar102 = (int)((long)uVar29 >> 0x21);
            iVar104 = *(int *)(*pauVar8 + 8) >> 1;
            uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar29 & 1)) & 0x100ffffff;
            iVar98 = -(int)uVar87;
            iVar100 = -(uint)(byte)(uVar87 >> 0x20);
            iVar103 = -(uint)(SUB121(*pauVar8,8) & 1);
            iVar98 = CONCAT13((char)((ulong)uVar29 >> 0x18) >> 1 ^ (byte)((uint)iVar98 >> 0x18),
                              CONCAT12((byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10),
                                       CONCAT11((byte)((uint)iVar99 >> 8) ^
                                                (byte)((uint)iVar98 >> 8),
                                                (byte)iVar99 ^ (byte)iVar98)));
            auVar91._0_8_ =
                 CONCAT17((byte)((long)uVar29 >> 0x39) ^ (byte)((uint)iVar100 >> 0x18),
                          CONCAT16((byte)((uint)iVar102 >> 0x10) ^ (byte)((uint)iVar100 >> 0x10),
                                   CONCAT15((byte)((uint)iVar102 >> 8) ^ (byte)((uint)iVar100 >> 8),
                                            CONCAT14((byte)iVar102 ^ (byte)iVar100,iVar98))));
            auVar91[8] = (byte)iVar104 ^ (byte)iVar103;
            auVar91[9] = (byte)((uint)iVar104 >> 8) ^ (byte)((uint)iVar103 >> 8);
            auVar91[10] = (byte)((uint)iVar104 >> 0x10) ^ (byte)((uint)iVar103 >> 0x10);
            auVar91[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar103 >> 0x18);
            *puVar6 = CONCAT44((int)((ulong)auVar91._0_8_ >> 0x20) + auVar74._4_4_,
                               iVar98 + auVar74._0_4_);
            *(int *)(puVar6 + 1) = auVar91._8_4_ + iVar101;
            *(undefined1 *)(lVar27 + lVar39) = 1;
          }
          uVar32 = iVar85 / 3;
          if (*(char *)(lVar26 + (int)uVar32) == '\0') {
            puVar25[iVar86] = uVar32;
            iVar86 = iVar86 + 1;
            *(undefined1 *)(lVar26 + (int)uVar32) = 1;
          }
        }
        iVar85 = *(int *)(lVar48 + (uVar31 + 2) * 4);
        if (iVar85 != -1) {
          lVar39 = (long)*(int *)(lVar42 + (long)iVar85 * 4);
          if (*(char *)(lVar27 + lVar39) == '\0') {
            pauVar8 = (undefined1 (*) [12])(lVar20 + (long)*(int *)(lVar42 + lVar30 * 0xc) * 0xc);
            puVar3 = (undefined8 *)
                     (lVar20 + (long)*(int *)(lVar42 + (-(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 |
                                                       (uVar31 & 0xffffffff) << 2) + 4) * 0xc);
            puVar4 = (undefined8 *)(lVar20 + (long)*(int *)(lVar42 + (uVar31 + 2) * 4) * 0xc);
            auVar93 = *pauVar8;
            uVar29 = *puVar3;
            uVar88 = *puVar4;
            auVar74._0_4_ = ((int)uVar29 + (int)*(undefined8 *)*pauVar8) - (int)uVar88;
            auVar74._4_4_ =
                 ((int)((ulong)uVar29 >> 0x20) + auVar93._4_4_) - (int)((ulong)uVar88 >> 0x20);
            auVar74._8_4_ = (*(int *)(puVar3 + 1) + auVar93._8_4_) - *(int *)(puVar4 + 1);
            auVar74._12_4_ = 0;
            puVar3 = (undefined8 *)(lVar20 + lVar39 * 0xc);
            pauVar8 = (undefined1 (*) [12])(lVar45 + lVar39 * 0xc);
            uVar29 = *(undefined8 *)*pauVar8;
            iVar103 = (int)uVar29 >> 1;
            iVar99 = (int)((long)uVar29 >> 0x21);
            iVar102 = *(int *)(*pauVar8 + 8) >> 1;
            uVar87 = CONCAT14(SUB121(*pauVar8,4),(uint)((byte)uVar29 & 1)) & 0x100ffffff;
            iVar101 = -(int)uVar87;
            iVar98 = -(uint)(byte)(uVar87 >> 0x20);
            iVar100 = -(uint)(SUB121(*pauVar8,8) & 1);
            iVar101 = CONCAT13((char)((ulong)uVar29 >> 0x18) >> 1 ^ (byte)((uint)iVar101 >> 0x18),
                               CONCAT12((byte)((uint)iVar103 >> 0x10) ^
                                        (byte)((uint)iVar101 >> 0x10),
                                        CONCAT11((byte)((uint)iVar103 >> 8) ^
                                                 (byte)((uint)iVar101 >> 8),
                                                 (byte)iVar103 ^ (byte)iVar101)));
            auVar92._0_8_ =
                 CONCAT17((byte)((long)uVar29 >> 0x39) ^ (byte)((uint)iVar98 >> 0x18),
                          CONCAT16((byte)((uint)iVar99 >> 0x10) ^ (byte)((uint)iVar98 >> 0x10),
                                   CONCAT15((byte)((uint)iVar99 >> 8) ^ (byte)((uint)iVar98 >> 8),
                                            CONCAT14((byte)iVar99 ^ (byte)iVar98,iVar101))));
            auVar92[8] = (byte)iVar102 ^ (byte)iVar100;
            auVar92[9] = (byte)((uint)iVar102 >> 8) ^ (byte)((uint)iVar100 >> 8);
            auVar92[10] = (byte)((uint)iVar102 >> 0x10) ^ (byte)((uint)iVar100 >> 0x10);
            auVar92[0xb] = (byte)(*(int *)(*pauVar8 + 8) >> 0x19) ^ (byte)((uint)iVar100 >> 0x18);
            *puVar3 = CONCAT44((int)((ulong)auVar92._0_8_ >> 0x20) + auVar74._4_4_,
                               iVar101 + auVar74._0_4_);
            *(int *)(puVar3 + 1) = auVar92._8_4_ + auVar74._8_4_;
            *(undefined1 *)(lVar27 + lVar39) = 1;
            iVar101 = auVar74._8_4_;
          }
          uVar32 = iVar85 / 3;
          if (*(char *)(lVar26 + (int)uVar32) == '\0') {
            puVar25[iVar86] = uVar32;
            iVar86 = iVar86 + 1;
            *(undefined1 *)(lVar26 + (int)uVar32) = 1;
          }
        }
        lVar54 = lVar54 + 1;
      } while (lVar54 < iVar86);
    }
LAB_1b7098fb4:
    if (0 < (int)uVar33) {
      if (uVar33 < 4) {
        uVar31 = 0;
      }
      else {
        lVar23 = 0;
        uVar31 = (ulong)uVar33 & 0x7ffffffc;
        uVar49 = uVar31;
        do {
          pauVar10 = (undefined1 (*) [16])(lVar20 + lVar23 * 0xc);
          auVar96 = NEON_scvtf(*pauVar10,4);
          auVar78 = NEON_scvtf(pauVar10[1],4);
          auVar68 = NEON_scvtf(pauVar10[2],4);
          auVar66._0_8_ = CONCAT44(auVar68._4_4_ * fVar64,auVar68._0_4_ * fVar64);
          auVar66._8_4_ = auVar68._8_4_ * fVar64;
          auVar66._12_4_ = auVar68._12_4_ * fVar64;
          auVar75._0_8_ = CONCAT44(auVar78._4_4_ * fVar64,auVar78._0_4_ * fVar64);
          auVar75._8_4_ = auVar78._8_4_ * fVar64;
          auVar75._12_4_ = auVar78._12_4_ * fVar64;
          auVar97._0_8_ = CONCAT44(auVar96._4_4_ * fVar64,auVar96._0_4_ * fVar64);
          auVar97._8_4_ = auVar96._8_4_ * fVar64;
          auVar97._12_4_ = auVar96._12_4_ * fVar64;
          *(long *)(*pauVar10 + 8) = auVar97._8_8_;
          *(undefined8 *)*pauVar10 = auVar97._0_8_;
          *(long *)(pauVar10[1] + 8) = auVar75._8_8_;
          *(undefined8 *)pauVar10[1] = auVar75._0_8_;
          *(long *)(pauVar10[2] + 8) = auVar66._8_8_;
          *(undefined8 *)pauVar10[2] = auVar66._0_8_;
          lVar23 = lVar23 + 4;
          uVar49 = uVar49 - 4;
        } while (uVar49 != 0);
        if (uVar31 == (long)(int)uVar33) goto LAB_1b7099550;
      }
      lVar23 = (long)(int)uVar33 - uVar31;
      do {
        pauVar8 = (undefined1 (*) [12])(lVar20 + uVar31 * 0xc);
        auVar67._12_4_ = 0;
        auVar67._0_12_ = *pauVar8;
        auVar68 = NEON_scvtf(auVar67,4);
        *(float *)(*pauVar8 + 8) = auVar68._8_4_ * fVar64;
        *(ulong *)*pauVar8 = CONCAT44(auVar68._4_4_ * fVar64,auVar68._0_4_ * fVar64);
        uVar31 = uVar31 + 1;
        lVar23 = lVar23 + -1;
      } while (lVar23 != 0);
    }
  }
LAB_1b7099550:
  func_0x0001b81206e0(puVar25);
  func_0x0001b81206e0(lVar26);
  func_0x0001b81206e0(lVar27);
  func_0x0001b81206e0(lVar45);
  param_15[1] = (long)((long)pfVar44 + (-param_15[1] - (long)param_1));
  if ((uStack_100 == 0) && (1 < (int)fVar63)) {
    lVar20 = (long)pfVar44 - (long)param_1;
    param_15[2] = lVar20;
    if (uVar37 != 0) {
      pfVar51 = (float *)((long)pfVar44 + 1);
      bVar13 = *(byte *)pfVar44;
      uVar33 = *param_4;
      pfVar44 = (float *)((long)pfVar44 + uVar37);
      uVar34 = (ulong)bVar13 & 0x3f;
      bVar18 = (bVar13 & 0x40) == 0;
      uVar31 = 6;
      uVar49 = uVar37 - 1;
      uVar35 = 1;
LAB_1b70995e0:
      uVar37 = uVar49;
      if (bVar18) {
        uVar35 = -(uint)uVar34;
        if (-1 < (char)bVar13) {
          uVar35 = (uint)uVar34;
        }
        if ((int)uVar35 < 1) {
          uStack_100 = 0;
          pfVar44 = pfVar51;
        }
        else {
          iVar101 = uVar33 * uVar35;
          uVar32 = iVar101 + 0xeU;
          if (-8 < iVar101) {
            uVar32 = iVar101 + 7;
          }
          lVar20 = (long)((ulong)uVar32 << 0x20) >> 0x23;
          lVar45 = func_0x0001b8120b80(lVar20,0x100004077774924);
          if (iVar101 + 0xeU < 0xf) {
            uStack_100 = 0;
          }
          else {
            auStack_b4._0_3_ = 0;
            uStack_b8 = 0;
            if (uVar37 == 0) {
              uVar31 = 0;
              pfVar44 = pfVar51;
LAB_1b7099dd4:
              pfVar51 = pfVar44;
              auStack_b4._0_3_ = 0;
              uStack_b8 = 0;
              uStack_100 = 2;
              uVar37 = uVar31;
            }
            else {
              pfVar44 = (float *)((long)pfVar51 + 1);
              bVar13 = *(byte *)pfVar51;
              uVar31 = uVar37 - 1;
              if ((ulong)bVar13 == 0xff) {
                bVar18 = uVar37 < 9;
                uVar37 = uVar37 - 9;
                if (bVar18) goto LAB_1b7099dd4;
                uStack_b8 = *(uint *)((long)pfVar51 + 2);
                uVar49 = (ulong)*(byte *)((long)pfVar51 + 1);
                uVar31 = (ulong)*(uint7 *)((long)pfVar51 + 2);
                auStack_b4[2] = *(byte *)(pfVar51 + 2);
                auStack_b4._0_2_ = (short)*(undefined3 *)((long)pfVar51 + 6);
                pfVar51 = (float *)((long)pfVar51 + 9);
              }
              else {
                iVar101 = 7;
                if ((bVar13 & 0x40) != 0) {
                  iVar101 = 8;
                }
                iVar86 = 6;
                if ((bVar13 & 0x20) != 0) {
                  iVar86 = iVar101;
                }
                iVar101 = 5;
                if ((bVar13 & 0x10) != 0) {
                  iVar101 = iVar86;
                }
                iVar86 = 4;
                if ((bVar13 & 8) != 0) {
                  iVar86 = iVar101;
                }
                iVar101 = 3;
                if ((bVar13 & 4) != 0) {
                  iVar101 = iVar86;
                }
                iVar86 = 2;
                if ((bVar13 & 2) != 0) {
                  iVar86 = iVar101;
                }
                iVar101 = 1;
                if ((bVar13 & 1) != 0) {
                  iVar101 = iVar86;
                }
                uVar49 = (ulong)(iVar101 - 1);
                uVar37 = uVar31 - uVar49;
                if (uVar31 < uVar49) goto LAB_1b7099dd4;
                func_0x0001b8120bb0(&uStack_b8,pfVar44,uVar49);
                pfVar51 = (float *)((long)pfVar44 + uVar49);
                uVar49 = ((ulong)uStack_b8 << 8 | (ulong)(uint3)auStack_b4._0_3_ << 0x28 |
                         (ulong)bVar13) >> iVar101;
                uVar31 = uVar49 >> 8;
                uStack_b8 = (uint)(uVar49 >> 8);
                auStack_b4._0_3_ = (undefined3)(uVar49 >> 0x28);
              }
              uVar31 = uVar49 & 0xff | uVar31 << 8;
              if ((lVar45 == 0) || (lVar23 = byet(pfVar51,uVar31,lVar45,lVar20,1), lVar23 == lVar20)
                 ) {
                if (uVar37 < uVar31) {
                  uStack_100 = 2;
                }
                else {
                  uStack_100 = 0;
                  pfVar51 = (float *)((long)pfVar51 + uVar31);
                  uVar37 = uVar37 - uVar31;
                }
              }
              else {
                uStack_100 = 0x80000000;
              }
            }
          }
          lVar20 = func_0x0001b8120b70((long)(int)uVar33,1,0x100004077774924);
          if (0 < (int)uVar33) {
            lVar23 = 0;
            iVar101 = 0;
            do {
              uVar32 = 0;
              uVar36 = (uint)*(byte *)(lVar20 + lVar23);
              do {
                uVar2 = iVar101 + uVar32;
                uVar11 = uVar2 + 7;
                if (-1 < (int)uVar2) {
                  uVar11 = uVar2;
                }
                uVar36 = uVar36 | (*(byte *)(lVar45 + ((int)uVar11 >> 3)) >> (ulong)(uVar2 & 7) & 1)
                                  << (ulong)(uVar32 & 0x1f);
                *(char *)(lVar20 + lVar23) = (char)uVar36;
                uVar32 = uVar32 + 1;
              } while (uVar35 != uVar32);
              iVar101 = iVar101 + uVar32;
              lVar23 = lVar23 + 1;
            } while (lVar23 != (int)uVar33);
          }
          *param_14 = lVar20;
          func_0x0001b81206e0(lVar45);
          lVar20 = param_15[2];
          pfVar44 = pfVar51;
        }
        goto LAB_1b7099804;
      }
      if (uVar37 == 0) {
        uStack_100 = 2;
        goto LAB_1b7099804;
      }
      pfVar53 = (float *)((long)pfVar51 + 1);
      bVar14 = *(byte *)pfVar51;
      if ((uVar35 != 9) || ((bVar14 & 0x7c) == 0)) goto LAB_1b70995fc;
      goto LAB_1b70997f4;
    }
    uStack_100 = 2;
LAB_1b7099804:
    param_15[2] = (long)pfVar44 - (long)(lVar20 + (long)param_1);
  }
  if (uStack_100 == 0) {
    if (uVar37 == 0) {
LAB_1b7099898:
      uStack_100 = 2;
    }
    else {
      uStack_230 = uVar37 - 1;
      uVar49 = (ulong)*(byte *)pfVar44 & 0x3f;
      bVar18 = (*(byte *)pfVar44 & 0x40) == 0;
      pfVar53 = (float *)((long)pfVar44 + uVar37);
      uVar31 = 6;
      pfVar51 = (float *)((long)pfVar44 + 1);
      uVar33 = 1;
      do {
        if (bVar18) {
          if (uVar49 == 0) {
            uStack_100 = 0;
            goto LAB_1b709b3d4;
          }
          param_15[3] = (long)pfVar51 - (long)param_1;
          lVar27 = *param_9;
          uVar33 = *param_4;
          uVar35 = *param_13;
          uVar37 = (ulong)(int)uVar35;
          lVar20 = func_0x0001b8120b70(uVar37,1,0x476c0bfe);
          lVar26 = (long)(int)uVar33 << 2;
          lVar45 = func_0x0001b8120b80(lVar26,0x100004052888210);
          lVar23 = func_0x0001b8120b80(lVar26,0x100004052888210);
          puVar28 = (undefined4 *)func_0x0001b8120b80(uVar37 << 2,0x100004052888210);
          uVar31 = -(ulong)(uVar35 * 3 >> 0x1f) & 0xfffffffc00000000 | (ulong)(uVar35 * 3) << 2;
          lVar42 = func_0x0001b8120b80(uVar31,0x100004052888210);
          lVar46 = func_0x0001b8120b80(uVar37 << 2,0x100004052888210);
          if (uStack_230 != 0) {
            uVar40 = uStack_230 - 2;
            bVar13 = *(byte *)pfVar51;
            uVar49 = uStack_230 - 1;
            uVar38 = (ulong)bVar13 & 0x3f;
            bVar18 = (bVar13 & 0x40) == 0;
            uVar34 = 6;
            pfVar47 = (float *)((long)pfVar51 + 1);
            uVar33 = 1;
            goto LAB_1b7099adc;
          }
          uVar49 = 0;
          uStack_100 = 2;
          goto LAB_1b7099e3c;
        }
        pfVar44 = pfVar53;
        if (uStack_230 == 0) goto LAB_1b7099898;
        pfVar44 = (float *)((long)pfVar51 + 1);
        bVar13 = *(byte *)pfVar51;
        if ((uVar33 == 9) && ((bVar13 & 0x7c) != 0)) break;
        bVar18 = (uint)(int)(char)bVar13 < 0x80000000;
        uVar49 = ((ulong)bVar13 & 0x7f) << (uVar31 & 0x3f) | uVar49;
        uVar31 = uVar31 + 7;
        uStack_230 = uStack_230 - 1;
        uVar35 = uVar33 + 1;
        bVar19 = uVar33 < 9;
        pfVar51 = pfVar44;
        uVar33 = uVar35;
      } while ((bVar19) || (-1 < (char)bVar13));
      uStack_100 = 0x10;
    }
  }
  goto LAB_1b7099b68;
LAB_1b7097c44:
  iVar101 = 0;
LAB_1b7097c4c:
  uStack_100 = 2;
  uVar49 = 0;
  pfVar44 = pfVar53;
  uVar31 = 0;
  goto LAB_1b709775c;
LAB_1b70995fc:
  bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
  uVar34 = ((ulong)bVar14 & 0x7f) << (uVar31 & 0x3f) | uVar34;
  uVar31 = uVar31 + 7;
  uVar32 = uVar35 + 1;
  bVar19 = uVar35 < 9;
  uVar49 = uVar37 - 1;
  pfVar51 = pfVar53;
  uVar35 = uVar32;
  if ((bVar19) || (-1 < (char)bVar14)) goto LAB_1b70995e0;
LAB_1b70997f4:
  uVar37 = uVar37 - 1;
  uStack_100 = 0x10;
  pfVar44 = pfVar53;
  goto LAB_1b7099804;
LAB_1b7099adc:
  if (bVar18) {
    bVar18 = false;
    uStack_100 = 0;
    uVar49 = uVar40 + 1;
    uVar33 = -(uint)uVar38;
    if (-1 < (char)bVar13) {
      uVar33 = (uint)uVar38;
    }
  }
  else if (uVar40 == 0xffffffffffffffff) {
    uVar49 = 0;
    uStack_100 = 2;
    bVar18 = true;
    pfVar47 = pfVar53;
    uVar33 = 0;
  }
  else {
    pfVar51 = (float *)((long)pfVar47 + 1);
    bVar14 = *(byte *)pfVar47;
    if ((uVar33 != 9) || ((bVar14 & 0x7c) == 0)) goto LAB_1b7099afc;
    uStack_100 = 0x10;
    uVar49 = uVar40;
LAB_1b7099e3c:
    bVar18 = true;
    pfVar47 = pfVar51;
    uVar33 = 0;
  }
  goto LAB_1b7099e40;
LAB_1b7099afc:
  bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
  uVar38 = ((ulong)bVar14 & 0x7f) << (uVar34 & 0x3f) | uVar38;
  uVar34 = uVar34 + 7;
  uVar40 = uVar40 - 1;
  uVar49 = uVar49 - 1;
  uVar32 = uVar33 + 1;
  bVar19 = uVar33 < 9;
  pfVar47 = pfVar51;
  uVar33 = uVar32;
  if ((bVar19) || (-1 < (char)bVar14)) goto LAB_1b7099adc;
  uStack_100 = 0x10;
  bVar18 = true;
  uVar33 = 0;
LAB_1b7099e40:
  *param_6 = uVar33;
  pfVar44 = pfVar47;
  if ((uVar35 + 2 < 3) || (bVar18)) {
    if (uStack_100 != 0) {
      lVar54 = 0;
      uStack_230 = uVar49;
      goto LAB_1b709a270;
    }
LAB_1b709a17c:
    if (uVar49 == 0) {
LAB_1b709a210:
      uStack_230 = 0;
      lVar54 = 0;
      uStack_100 = 2;
      pfVar44 = pfVar47;
    }
    else {
      pfVar44 = (float *)((long)pfVar47 + 1);
      bVar13 = *(byte *)pfVar47;
      uVar40 = (ulong)bVar13 & 0x3f;
      bVar18 = (bVar13 & 0x40) == 0;
      pfVar47 = (float *)((long)pfVar47 + uVar49);
      uVar34 = 6;
      uVar49 = uVar49 - 1;
      uVar33 = 1;
      do {
        uStack_230 = uVar49;
        if (bVar18) {
          uStack_100 = 0;
          uVar49 = (ulong)(uint)-(int)uVar40;
          if (-1 < (char)bVar13) {
            uVar49 = uVar40;
          }
          lVar54 = uVar49 << 0x20;
          goto LAB_1b709a270;
        }
        if (uStack_230 == 0) goto LAB_1b709a210;
        pfVar51 = (float *)((long)pfVar44 + 1);
        bVar14 = *(byte *)pfVar44;
        pfVar44 = pfVar51;
        if ((uVar33 == 9) && ((bVar14 & 0x7c) != 0)) break;
        bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
        uVar40 = ((ulong)bVar14 & 0x7f) << (uVar34 & 0x3f) | uVar40;
        uVar34 = uVar34 + 7;
        uVar32 = uVar33 + 1;
        bVar19 = uVar33 < 9;
        uVar49 = uStack_230 - 1;
        uVar33 = uVar32;
      } while ((bVar19) || (-1 < (char)bVar14));
      uStack_230 = uStack_230 - 1;
      lVar54 = 0;
      uStack_100 = 0x10;
    }
  }
  else {
    auStack_ac._0_3_ = 0;
    uStack_b0 = 0;
    if (uVar49 == 0) {
      uVar34 = 0;
LAB_1b7099f0c:
      lVar54 = 0;
      auStack_ac._0_3_ = 0;
      uStack_100 = 2;
      uStack_b0 = 0;
      uStack_230 = uVar34;
    }
    else {
      pfVar44 = (float *)((long)pfVar47 + 1);
      bVar13 = *(byte *)pfVar47;
      uVar34 = uVar49 - 1;
      if ((ulong)bVar13 == 0xff) {
        uStack_230 = uVar49 - 9;
        if (8 < uVar49) {
          uStack_b0 = *(uint *)((long)pfVar47 + 2);
          uVar34 = (ulong)*(byte *)((long)pfVar47 + 1);
          uVar49 = (ulong)*(uint7 *)((long)pfVar47 + 2);
          auStack_ac[2] = *(byte *)(pfVar47 + 2);
          auStack_ac._0_2_ = (short)*(undefined3 *)((long)pfVar47 + 6);
          pfVar44 = (float *)((long)pfVar47 + 9);
          goto LAB_1b709a114;
        }
LAB_1b709a164:
        uStack_230 = uVar34;
        uStack_100 = 2;
      }
      else {
        iVar101 = 7;
        if ((bVar13 & 0x40) != 0) {
          iVar101 = 8;
        }
        iVar86 = 6;
        if ((bVar13 & 0x20) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 5;
        if ((bVar13 & 0x10) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 4;
        if ((bVar13 & 8) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 3;
        if ((bVar13 & 4) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 2;
        if ((bVar13 & 2) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 1;
        if ((bVar13 & 1) != 0) {
          iVar101 = iVar86;
        }
        uVar49 = (ulong)(iVar101 - 1);
        uStack_230 = uVar34 - uVar49;
        if (uVar34 < uVar49) goto LAB_1b7099f0c;
        func_0x0001b8120bb0(&uStack_b0,pfVar44,uVar49);
        pfVar44 = (float *)((long)pfVar44 + uVar49);
        uVar34 = ((ulong)uStack_b0 << 8 | (ulong)(uint3)auStack_ac._0_3_ << 0x28 | (ulong)bVar13) >>
                 iVar101;
        uVar49 = uVar34 >> 8;
        uStack_b0 = (uint)(uVar34 >> 8);
        auStack_ac._0_3_ = (undefined3)(uVar34 >> 0x28);
LAB_1b709a114:
        uVar40 = uVar34 & 0xff | uVar49 << 8;
        if (lVar20 == 0) {
LAB_1b709a158:
          uVar49 = uStack_230 - uVar40;
          uVar34 = uStack_230;
          if (uVar40 <= uStack_230) {
            pfVar47 = (float *)((long)pfVar44 + uVar40);
            goto LAB_1b709a17c;
          }
          goto LAB_1b709a164;
        }
        iVar101 = uVar35 + 1;
        uVar33 = iVar101 - (iVar101 >> 0x1f);
        uStack_100 = iVar101 / 2;
        iStack_fc = (int)uVar33 >> 0x1f;
        lVar54 = byet(pfVar44,uVar40,lVar20,(long)((ulong)uVar33 << 0x20) >> 0x21,1);
        if (lVar54 == CONCAT44(iStack_fc,uStack_100)) goto LAB_1b709a158;
        uStack_100 = 0x80000000;
      }
      lVar54 = 0;
    }
  }
LAB_1b709a270:
  lVar30 = func_0x0001b8120b80(lVar54 >> 0x1e,0x100004052888210);
  if ((lVar54 != 0) && (uStack_100 == 0)) {
    auStack_a4._0_3_ = 0;
    uStack_a8 = 0;
    if (uStack_230 == 0) {
      uStack_230 = 0;
LAB_1b709a33c:
      auStack_a4._0_3_ = 0;
      uStack_100 = 2;
      uStack_a8 = 0;
    }
    else {
      pfVar51 = (float *)((long)pfVar44 + 1);
      bVar13 = *(byte *)pfVar44;
      uVar49 = uStack_230 - 1;
      if ((ulong)bVar13 == 0xff) {
        uVar34 = uStack_230 - 9;
        if (uStack_230 < 9) {
          uStack_100 = 2;
          pfVar44 = pfVar51;
          uStack_230 = uVar49;
          goto LAB_1b709a354;
        }
        uStack_a8 = *(uint *)((long)pfVar44 + 2);
        uVar40 = (ulong)*(byte *)((long)pfVar44 + 1);
        uVar49 = (ulong)*(uint7 *)((long)pfVar44 + 2);
        auStack_a4[2] = *(byte *)(pfVar44 + 2);
        auStack_a4._0_2_ = (short)*(undefined3 *)((long)pfVar44 + 6);
        pfVar44 = (float *)((long)pfVar44 + 9);
      }
      else {
        iVar101 = 7;
        if ((bVar13 & 0x40) != 0) {
          iVar101 = 8;
        }
        iVar86 = 6;
        if ((bVar13 & 0x20) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 5;
        if ((bVar13 & 0x10) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 4;
        if ((bVar13 & 8) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 3;
        if ((bVar13 & 4) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 2;
        if ((bVar13 & 2) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 1;
        if ((bVar13 & 1) != 0) {
          iVar101 = iVar86;
        }
        uVar40 = (ulong)(iVar101 - 1);
        uVar34 = uVar49 - uVar40;
        pfVar44 = pfVar51;
        uStack_230 = uVar49;
        if (uVar49 < uVar40) goto LAB_1b709a33c;
        func_0x0001b8120bb0(&uStack_a8,pfVar51,uVar40);
        pfVar44 = (float *)((long)pfVar51 + uVar40);
        uVar40 = ((ulong)uStack_a8 << 8 | (ulong)(uint3)auStack_a4._0_3_ << 0x28 | (ulong)bVar13) >>
                 iVar101;
        uVar49 = uVar40 >> 8;
        uStack_a8 = (uint)(uVar40 >> 8);
        auStack_a4._0_3_ = (undefined3)(uVar40 >> 0x28);
      }
      uVar49 = uVar40 & 0xff | uVar49 << 8;
      uStack_230 = uVar34;
      if ((lVar30 == 0) ||
         (lVar39 = byet(pfVar44,uVar49,lVar30,lVar54 >> 0x20,4), lVar39 == lVar54 >> 0x20)) {
        if (uVar34 < uVar49) {
          uStack_100 = 2;
        }
        else {
          uStack_100 = 0;
          pfVar44 = (float *)((long)pfVar44 + uVar49);
          uStack_230 = uVar34 - uVar49;
        }
      }
      else {
        uStack_100 = 0x80000000;
      }
    }
  }
LAB_1b709a354:
  if ((uVar37 & 1) == 0) {
    uVar33 = (int)uVar35 >> 1;
  }
  else {
    uVar33 = (int)uVar35 / 2;
    *(undefined1 *)(lVar20 + (uVar37 - 1)) = *(undefined1 *)(lVar20 + (int)uVar33);
  }
  uVar49 = (ulong)uVar33;
  if ((int)uVar35 < 2) {
    if (uVar35 != 1) {
      func_0x0001b8120bd0(lVar42,0xff,uVar31);
      func_0x0001b8120bd0(lVar45,0xff,lVar26);
      uVar33 = 0;
LAB_1b709a420:
      *param_10 = lVar42;
      *param_12 = lVar46;
      *param_6 = uVar33;
      func_0x0001b81206e0(lVar20);
      func_0x0001b81206e0(lVar45);
      func_0x0001b81206e0(lVar23);
      func_0x0001b81206e0(puVar28);
      func_0x0001b81206e0(lVar30);
      param_15[3] = (long)((long)pfVar44 + (-param_15[3] - (long)param_1));
      if (uStack_100 != 0) goto LAB_1b7099b68;
      lVar20 = func_0x0001b8120b80((long)(int)*param_6 << 3,0x100004000313f17);
      *param_5 = lVar20;
      param_15[4] = (long)pfVar44 - (long)param_1;
      uVar33 = *param_6;
      uVar37 = (ulong)(int)uVar33;
      lVar26 = *param_10;
      uVar35 = *param_13;
      lVar46 = (long)(int)uVar35;
      lVar45 = func_0x0001b8120b80(uVar37 << 3,0x100004000313f17);
      uVar31 = (ulong)(uVar35 * 3);
      lVar23 = func_0x0001b8120b80(-(ulong)(uVar35 * 3 >> 0x1f) & 0xfffffffc00000000 | uVar31 << 2,
                                   0x100004052888210);
      lVar42 = func_0x0001b8120b70(uVar37,0x20,0x1020040a5b76cdf);
      if (0 < (int)uVar35) {
        func_0x0001b8120bd0(lVar23,0xff,uVar31 << 2);
        if (lVar42 == 0) {
          uVar49 = 0;
          do {
            lVar27 = (long)*(int *)(lVar26 + uVar49 * 4) << 5;
            do {
              lVar54 = lVar27;
              iVar101 = *(int *)(lVar54 + 0x14);
              lVar27 = lVar54;
              if (iVar101 != 5) goto LAB_1b709abb4;
              lVar27 = *(long *)(lVar54 + 0x18);
            } while (*(long *)(lVar54 + 0x18) != 0);
            lVar27 = func_0x0001b8120b70(1,0x20,0x1020040a5b76cdf);
            *(long *)(lVar54 + 0x18) = lVar27;
            iVar101 = *(int *)(lVar27 + 0x14);
LAB_1b709abb4:
            *(int *)(lVar27 + 0x14) = iVar101 + 1;
            *(int *)(lVar27 + (long)iVar101 * 4) = (int)uVar49;
            uVar49 = uVar49 + 1;
          } while (uVar49 != uVar31);
        }
        else {
          uVar49 = 0;
          do {
            iVar86 = *(int *)(lVar26 + uVar49 * 4);
            iVar101 = (uint)(uVar49 * 0xaaaaaaab >> 0x21) * 3;
            uVar34 = uVar49 + 1;
            lVar27 = lVar42 + (long)*(int *)(lVar26 + (long)(int)(iVar101 +
                                                                 (int)uVar34 +
                                                                 (uint)(uVar49 * 0xaaaaaaab +
                                                                        0xaaaaaaab >> 0x21) * -3) *
                                                      4) * 0x20;
            iVar101 = iVar101 + ((int)uVar49 + 2U) % 3;
            do {
              iVar85 = *(int *)(lVar27 + 0x14);
              if (iVar85 < 1) {
                iVar98 = 0;
              }
              else {
                lVar54 = 0;
                iVar98 = 0;
                do {
                  iVar85 = *(int *)(lVar27 + lVar54 * 4);
                  iVar100 = (iVar85 / 3) * 3;
                  if (*(int *)(lVar26 + (long)(iVar100 + (iVar85 + 1) % 3) * 4) == iVar86) {
                    *(int *)(lVar23 + (long)(iVar100 + (iVar85 + 2) % 3) * 4) = iVar101;
                    iVar85 = *(int *)(lVar27 + lVar54 * 4);
                    *(int *)(lVar23 + (long)iVar101 * 4) = (iVar85 / 3) * 3 + (iVar85 + 2) % 3;
                  }
                  else {
                    *(int *)(lVar27 + (long)iVar98 * 4) = iVar85;
                    iVar98 = iVar98 + 1;
                  }
                  lVar54 = lVar54 + 1;
                  iVar85 = *(int *)(lVar27 + 0x14);
                } while (lVar54 < iVar85);
              }
              if (iVar98 < iVar85) {
                *(int *)(lVar27 + 0x14) = iVar98;
                goto joined_r0x0001b709a57c;
              }
              lVar27 = *(long *)(lVar27 + 0x18);
              lVar54 = lVar42 + (long)iVar86 * 0x20;
            } while (lVar27 != 0);
            do {
              lVar30 = lVar54;
              iVar101 = *(int *)(lVar30 + 0x14);
              lVar27 = lVar30;
              if (iVar101 != 5) goto LAB_1b709a708;
              lVar54 = *(long *)(lVar30 + 0x18);
            } while (*(long *)(lVar30 + 0x18) != 0);
            lVar27 = func_0x0001b8120b70(1,0x20,0x1020040a5b76cdf);
            *(long *)(lVar30 + 0x18) = lVar27;
            iVar101 = *(int *)(lVar27 + 0x14);
LAB_1b709a708:
            *(int *)(lVar27 + 0x14) = iVar101 + 1;
            *(int *)(lVar27 + (long)iVar101 * 4) = (int)uVar49;
joined_r0x0001b709a57c:
            uVar49 = uVar34;
          } while (uVar34 != uVar31);
        }
      }
      if (0 < (int)uVar33) {
        uVar31 = 0;
        do {
          plVar50 = (long *)(lVar42 + uVar31 * 0x20 + 0x18);
          lVar27 = *plVar50;
          while (lVar27 != 0) {
            *plVar50 = *(long *)(lVar27 + 0x18);
            func_0x0001b81206e0();
            lVar27 = *plVar50;
          }
          uVar31 = uVar31 + 1;
        } while (uVar31 != uVar37);
      }
      func_0x0001b81206e0(lVar42);
      pfVar51 = pfVar44;
      if (uVar33 == 0) {
        uStack_100 = 0;
      }
      else {
        auStack_9c._0_3_ = 0;
        uStack_a0 = 0;
        if (uStack_230 == 0) {
          uVar31 = 0;
LAB_1b709abfc:
          auStack_9c._0_3_ = 0;
          uStack_100 = 2;
          uStack_a0 = 0;
          uStack_230 = uVar31;
        }
        else {
          pfVar51 = (float *)((long)pfVar44 + 1);
          bVar13 = *(byte *)pfVar44;
          uVar31 = uStack_230 - 1;
          if ((ulong)bVar13 == 0xff) {
            uVar49 = uStack_230 - 9;
            if (uStack_230 < 9) {
              uStack_100 = 2;
              uStack_230 = uVar31;
              goto LAB_1b709ac20;
            }
            uStack_a0 = *(uint *)((long)pfVar44 + 2);
            uVar34 = (ulong)*(byte *)((long)pfVar44 + 1);
            uVar31 = (ulong)*(uint7 *)((long)pfVar44 + 2);
            auStack_9c[2] = *(byte *)(pfVar44 + 2);
            auStack_9c._0_2_ = (short)*(undefined3 *)((long)pfVar44 + 6);
            pfVar51 = (float *)((long)pfVar44 + 9);
          }
          else {
            iVar101 = 7;
            if ((bVar13 & 0x40) != 0) {
              iVar101 = 8;
            }
            iVar86 = 6;
            if ((bVar13 & 0x20) != 0) {
              iVar86 = iVar101;
            }
            iVar101 = 5;
            if ((bVar13 & 0x10) != 0) {
              iVar101 = iVar86;
            }
            iVar86 = 4;
            if ((bVar13 & 8) != 0) {
              iVar86 = iVar101;
            }
            iVar101 = 3;
            if ((bVar13 & 4) != 0) {
              iVar101 = iVar86;
            }
            iVar86 = 2;
            if ((bVar13 & 2) != 0) {
              iVar86 = iVar101;
            }
            iVar101 = 1;
            if ((bVar13 & 1) != 0) {
              iVar101 = iVar86;
            }
            uVar34 = (ulong)(iVar101 - 1);
            uVar49 = uVar31 - uVar34;
            if (uVar31 < uVar34) goto LAB_1b709abfc;
            func_0x0001b8120bb0(&uStack_a0,pfVar51,uVar34);
            pfVar51 = (float *)((long)pfVar51 + uVar34);
            uVar34 = ((ulong)uStack_a0 << 8 | (ulong)(uint3)auStack_9c._0_3_ << 0x28 | (ulong)bVar13
                     ) >> iVar101;
            uVar31 = uVar34 >> 8;
            uStack_a0 = (uint)(uVar34 >> 8);
            auStack_9c._0_3_ = (undefined3)(uVar34 >> 0x28);
          }
          uVar31 = uVar34 & 0xff | uVar31 << 8;
          uStack_230 = uVar49;
          if ((lVar45 == 0) || (uVar34 = byet(pfVar51,uVar31,lVar45,uVar37,8), uVar34 == uVar37)) {
            if (uVar49 < uVar31) {
              uStack_100 = 2;
            }
            else {
              uStack_100 = 0;
              uStack_230 = uVar49 - uVar31;
              pfVar51 = (float *)((long)pfVar51 + uVar31);
            }
          }
          else {
            uStack_100 = 0x80000000;
          }
        }
      }
LAB_1b709ac20:
      puVar25 = (uint *)func_0x0001b8120b80(lVar46 << 2,0x100004052888210);
      if (fVar63 == 0.0) {
        lVar27 = func_0x0001b8120b70(lVar46,1,0xad8d04ae);
        lVar54 = func_0x0001b8120b70(uVar37,1,0xa95ddac6);
        iVar101 = 0;
        lVar42 = 0;
        fVar64 = 0.0;
        fVar56 = 0.0;
        while( true ) {
          if ((int)lVar42 < (int)uVar35) {
            lVar42 = (long)(int)lVar42;
            while (*(char *)(lVar27 + lVar42) != '\0') {
              lVar42 = lVar42 + 1;
              if (lVar46 == lVar42) goto LAB_1b709b380;
            }
          }
          uVar33 = (uint)lVar42;
          if (uVar33 == uVar35) break;
          lVar30 = (long)(int)uVar33 + (long)(int)uVar33 * 2;
          lVar43 = (long)(int)lVar30 * 4;
          lVar39 = (long)*(int *)(lVar26 + lVar43);
          lVar41 = (long)*(int *)(lVar26 + lVar30 * 4 + 4);
          lVar30 = (long)*(int *)(lVar26 + lVar43 + 8);
          if (*(char *)(lVar54 + lVar39) == '\0') {
            uVar31 = *(ulong *)(lVar45 + lVar39 * 8);
            iVar98 = (int)uVar31 >> 1;
            iVar100 = (int)((long)uVar31 >> 0x21);
            iVar86 = -(int)(uVar31 & 0x100000001);
            iVar85 = -(int)((uVar31 & 0x100000001) >> 0x20);
            uVar29 = NEON_scvtf(CONCAT17((byte)((long)uVar31 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18)
                                         ,CONCAT16((byte)((uint)iVar100 >> 0x10) ^
                                                   (byte)((uint)iVar85 >> 0x10),
                                                   CONCAT15((byte)((uint)iVar100 >> 8) ^
                                                            (byte)((uint)iVar85 >> 8),
                                                            CONCAT14((byte)iVar100 ^ (byte)iVar85,
                                                                     CONCAT13((char)(uVar31 >> 0x18)
                                                                              >> 1 ^ (byte)((uint)
                                                  iVar86 >> 0x18),
                                                  CONCAT12((byte)((uint)iVar98 >> 0x10) ^
                                                           (byte)((uint)iVar86 >> 0x10),
                                                           CONCAT11((byte)((uint)iVar98 >> 8) ^
                                                                    (byte)((uint)iVar86 >> 8),
                                                                    (byte)iVar98 ^ (byte)iVar86)))))
                                                  )),4);
            *(ulong *)(lVar20 + lVar39 * 8) =
                 CONCAT44(fVar56 + (float)((ulong)uVar29 >> 0x20) * fVar72,
                          fVar64 + (float)uVar29 * fVar72);
            *(undefined1 *)(lVar54 + lVar39) = 1;
            if (*(char *)(lVar54 + lVar41) == '\0') goto LAB_1b709b2a4;
LAB_1b709b06c:
            cVar15 = *(char *)(lVar54 + lVar30);
          }
          else {
            if (*(char *)(lVar54 + lVar41) != '\0') goto LAB_1b709b06c;
LAB_1b709b2a4:
            pfVar44 = (float *)(lVar20 + lVar39 * 8);
            fVar64 = *pfVar44;
            fVar56 = pfVar44[1];
            uVar31 = *(ulong *)(lVar45 + lVar41 * 8);
            iVar98 = (int)uVar31 >> 1;
            iVar100 = (int)((long)uVar31 >> 0x21);
            iVar86 = -(int)(uVar31 & 0x100000001);
            iVar85 = -(int)((uVar31 & 0x100000001) >> 0x20);
            uVar29 = NEON_scvtf(CONCAT17((byte)((long)uVar31 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18)
                                         ,CONCAT16((byte)((uint)iVar100 >> 0x10) ^
                                                   (byte)((uint)iVar85 >> 0x10),
                                                   CONCAT15((byte)((uint)iVar100 >> 8) ^
                                                            (byte)((uint)iVar85 >> 8),
                                                            CONCAT14((byte)iVar100 ^ (byte)iVar85,
                                                                     CONCAT13((char)(uVar31 >> 0x18)
                                                                              >> 1 ^ (byte)((uint)
                                                  iVar86 >> 0x18),
                                                  CONCAT12((byte)((uint)iVar98 >> 0x10) ^
                                                           (byte)((uint)iVar86 >> 0x10),
                                                           CONCAT11((byte)((uint)iVar98 >> 8) ^
                                                                    (byte)((uint)iVar86 >> 8),
                                                                    (byte)iVar98 ^ (byte)iVar86)))))
                                                  )),4);
            *(ulong *)(lVar20 + lVar41 * 8) =
                 CONCAT44(fVar56 + (float)((ulong)uVar29 >> 0x20) * fVar72,
                          fVar64 + (float)uVar29 * fVar72);
            *(undefined1 *)(lVar54 + lVar41) = 1;
            cVar15 = *(char *)(lVar54 + lVar30);
          }
          if (cVar15 == '\0') {
            uVar29 = *(undefined8 *)(lVar20 + lVar41 * 8);
            uVar88 = *(undefined8 *)(lVar20 + lVar39 * 8);
            uVar31 = *(ulong *)(lVar45 + lVar30 * 8);
            fVar64 = ((float)uVar88 + (float)uVar29) * SUB164(ZEXT816(0x3f0000003f000000),0);
            fVar56 = ((float)((ulong)uVar88 >> 0x20) + (float)((ulong)uVar29 >> 0x20)) *
                     SUB164(ZEXT816(0x3f0000003f000000),4);
            iVar98 = (int)uVar31 >> 1;
            iVar100 = (int)((long)uVar31 >> 0x21);
            iVar86 = -(int)(uVar31 & 0x100000001);
            iVar85 = -(int)((uVar31 & 0x100000001) >> 0x20);
            uVar29 = NEON_scvtf(CONCAT17((byte)((long)uVar31 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18)
                                         ,CONCAT16((byte)((uint)iVar100 >> 0x10) ^
                                                   (byte)((uint)iVar85 >> 0x10),
                                                   CONCAT15((byte)((uint)iVar100 >> 8) ^
                                                            (byte)((uint)iVar85 >> 8),
                                                            CONCAT14((byte)iVar100 ^ (byte)iVar85,
                                                                     CONCAT13((char)(uVar31 >> 0x18)
                                                                              >> 1 ^ (byte)((uint)
                                                  iVar86 >> 0x18),
                                                  CONCAT12((byte)((uint)iVar98 >> 0x10) ^
                                                           (byte)((uint)iVar86 >> 0x10),
                                                           CONCAT11((byte)((uint)iVar98 >> 8) ^
                                                                    (byte)((uint)iVar86 >> 8),
                                                                    (byte)iVar98 ^ (byte)iVar86)))))
                                                  )),4);
            *(ulong *)(lVar20 + lVar30 * 8) =
                 CONCAT44(fVar56 + (float)((ulong)uVar29 >> 0x20) * fVar72,
                          fVar64 + (float)uVar29 * fVar72);
            *(undefined1 *)(lVar54 + lVar30) = 1;
          }
          lVar30 = 0;
          puVar25[iVar101] = uVar33;
          iVar101 = 1;
          *(undefined1 *)(lVar27 + (int)uVar33) = 1;
          do {
            lVar39 = (long)(int)puVar25[lVar30];
            uVar31 = lVar39 * 3;
            iVar86 = *(int *)(lVar23 + lVar39 * 0xc);
            if (iVar86 != -1) {
              lVar41 = (long)*(int *)(lVar26 + (long)iVar86 * 4);
              if (*(char *)(lVar54 + lVar41) == '\0') {
                uVar37 = -(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 | (uVar31 & 0xffffffff) << 2;
                uVar29 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + uVar37 + 4) * 8);
                uVar88 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + uVar37 + 8) * 8);
                uVar89 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + lVar39 * 0xc) * 8);
                uVar37 = *(ulong *)(lVar45 + lVar41 * 8);
                fVar64 = ((float)uVar88 + (float)uVar29) - (float)uVar89;
                fVar56 = ((float)((ulong)uVar88 >> 0x20) + (float)((ulong)uVar29 >> 0x20)) -
                         (float)((ulong)uVar89 >> 0x20);
                iVar85 = (int)uVar37 >> 1;
                iVar98 = (int)((long)uVar37 >> 0x21);
                iVar100 = -(int)(uVar37 & 0x100000001);
                iVar103 = -(int)((uVar37 & 0x100000001) >> 0x20);
                uVar29 = NEON_scvtf(CONCAT17((byte)((long)uVar37 >> 0x39) ^
                                             (byte)((uint)iVar103 >> 0x18),
                                             CONCAT16((byte)((uint3)(int3)((long)uVar37 >> 0x29) >>
                                                            8) ^ (byte)((uint)iVar103 >> 0x10),
                                                      CONCAT15((byte)((uint)iVar98 >> 8) ^
                                                               (byte)((uint)iVar103 >> 8),
                                                               CONCAT14((byte)iVar98 ^ (byte)iVar103
                                                                        ,CONCAT13((char)(uVar37 >>
                                                                                        0x18) >> 1 ^
                                                                                  (byte)((uint)
                                                  iVar100 >> 0x18),
                                                  CONCAT12((byte)((uint)iVar85 >> 0x10) ^
                                                           (byte)((uint)iVar100 >> 0x10),
                                                           CONCAT11((byte)((uint)iVar85 >> 8) ^
                                                                    (byte)((uint)iVar100 >> 8),
                                                                    (byte)iVar85 ^ (byte)iVar100))))
                                                  ))),4);
                *(ulong *)(lVar20 + lVar41 * 8) =
                     CONCAT44(fVar56 + (float)((ulong)uVar29 >> 0x20) * fVar72,
                              fVar64 + (float)uVar29 * fVar72);
                *(undefined1 *)(lVar54 + lVar41) = 1;
              }
              uVar33 = iVar86 / 3;
              if (*(char *)(lVar27 + (int)uVar33) == '\0') {
                puVar25[iVar101] = uVar33;
                iVar101 = iVar101 + 1;
                *(undefined1 *)(lVar27 + (int)uVar33) = 1;
              }
            }
            iVar86 = *(int *)(lVar23 + (uVar31 + 1) * 4);
            if (iVar86 != -1) {
              lVar41 = (long)*(int *)(lVar26 + (long)iVar86 * 4);
              if (*(char *)(lVar54 + lVar41) == '\0') {
                uVar29 = *(undefined8 *)
                          (lVar20 + (long)*(int *)(lVar26 + (-(uVar31 >> 0x1f & 1) &
                                                             0xfffffffc00000000 |
                                                            (uVar31 & 0xffffffff) << 2) + 8) * 8);
                uVar88 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + lVar39 * 0xc) * 8);
                uVar89 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + (uVar31 + 1) * 4) * 8);
                uVar37 = *(ulong *)(lVar45 + lVar41 * 8);
                fVar64 = ((float)uVar88 + (float)uVar29) - (float)uVar89;
                fVar56 = ((float)((ulong)uVar88 >> 0x20) + (float)((ulong)uVar29 >> 0x20)) -
                         (float)((ulong)uVar89 >> 0x20);
                iVar85 = (int)uVar37 >> 1;
                iVar98 = (int)((long)uVar37 >> 0x21);
                iVar100 = -(int)(uVar37 & 0x100000001);
                iVar103 = -(int)((uVar37 & 0x100000001) >> 0x20);
                uVar29 = NEON_scvtf(CONCAT17((byte)((long)uVar37 >> 0x39) ^
                                             (byte)((uint)iVar103 >> 0x18),
                                             CONCAT16((byte)((uint3)(int3)((long)uVar37 >> 0x29) >>
                                                            8) ^ (byte)((uint)iVar103 >> 0x10),
                                                      CONCAT15((byte)((uint)iVar98 >> 8) ^
                                                               (byte)((uint)iVar103 >> 8),
                                                               CONCAT14((byte)iVar98 ^ (byte)iVar103
                                                                        ,CONCAT13((char)(uVar37 >>
                                                                                        0x18) >> 1 ^
                                                                                  (byte)((uint)
                                                  iVar100 >> 0x18),
                                                  CONCAT12((byte)((uint)iVar85 >> 0x10) ^
                                                           (byte)((uint)iVar100 >> 0x10),
                                                           CONCAT11((byte)((uint)iVar85 >> 8) ^
                                                                    (byte)((uint)iVar100 >> 8),
                                                                    (byte)iVar85 ^ (byte)iVar100))))
                                                  ))),4);
                *(ulong *)(lVar20 + lVar41 * 8) =
                     CONCAT44(fVar56 + (float)((ulong)uVar29 >> 0x20) * fVar72,
                              fVar64 + (float)uVar29 * fVar72);
                *(undefined1 *)(lVar54 + lVar41) = 1;
              }
              uVar33 = iVar86 / 3;
              if (*(char *)(lVar27 + (int)uVar33) == '\0') {
                puVar25[iVar101] = uVar33;
                iVar101 = iVar101 + 1;
                *(undefined1 *)(lVar27 + (int)uVar33) = 1;
              }
            }
            iVar86 = *(int *)(lVar23 + (uVar31 + 2) * 4);
            if (iVar86 != -1) {
              lVar41 = (long)*(int *)(lVar26 + (long)iVar86 * 4);
              if (*(char *)(lVar54 + lVar41) == '\0') {
                uVar29 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + lVar39 * 0xc) * 8);
                uVar88 = *(undefined8 *)
                          (lVar20 + (long)*(int *)(lVar26 + (-(uVar31 >> 0x1f & 1) &
                                                             0xfffffffc00000000 |
                                                            (uVar31 & 0xffffffff) << 2) + 4) * 8);
                uVar89 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + (uVar31 + 2) * 4) * 8);
                uVar31 = *(ulong *)(lVar45 + lVar41 * 8);
                fVar64 = ((float)uVar88 + (float)uVar29) - (float)uVar89;
                fVar56 = ((float)((ulong)uVar88 >> 0x20) + (float)((ulong)uVar29 >> 0x20)) -
                         (float)((ulong)uVar89 >> 0x20);
                iVar85 = (int)uVar31 >> 1;
                iVar98 = (int)((long)uVar31 >> 0x21);
                iVar100 = -(int)(uVar31 & 0x100000001);
                iVar103 = -(int)((uVar31 & 0x100000001) >> 0x20);
                uVar29 = NEON_scvtf(CONCAT17((byte)((long)uVar31 >> 0x39) ^
                                             (byte)((uint)iVar103 >> 0x18),
                                             CONCAT16((byte)((uint3)(int3)((long)uVar31 >> 0x29) >>
                                                            8) ^ (byte)((uint)iVar103 >> 0x10),
                                                      CONCAT15((byte)((uint)iVar98 >> 8) ^
                                                               (byte)((uint)iVar103 >> 8),
                                                               CONCAT14((byte)iVar98 ^ (byte)iVar103
                                                                        ,CONCAT13((char)(uVar31 >>
                                                                                        0x18) >> 1 ^
                                                                                  (byte)((uint)
                                                  iVar100 >> 0x18),
                                                  CONCAT12((byte)((uint)iVar85 >> 0x10) ^
                                                           (byte)((uint)iVar100 >> 0x10),
                                                           CONCAT11((byte)((uint)iVar85 >> 8) ^
                                                                    (byte)((uint)iVar100 >> 8),
                                                                    (byte)iVar85 ^ (byte)iVar100))))
                                                  ))),4);
                *(ulong *)(lVar20 + lVar41 * 8) =
                     CONCAT44(fVar56 + (float)((ulong)uVar29 >> 0x20) * fVar72,
                              fVar64 + (float)uVar29 * fVar72);
                *(undefined1 *)(lVar54 + lVar41) = 1;
              }
              uVar33 = iVar86 / 3;
              if (*(char *)(lVar27 + (int)uVar33) == '\0') {
                puVar25[iVar101] = uVar33;
                iVar101 = iVar101 + 1;
                *(undefined1 *)(lVar27 + (int)uVar33) = 1;
              }
            }
            lVar30 = lVar30 + 1;
          } while (lVar30 < iVar101);
        }
      }
      else {
        lVar27 = func_0x0001b8120b70(lVar46,1,0x5668e67b);
        lVar54 = func_0x0001b8120b70(uVar37,1,0x5fd20a74);
        lVar42 = 0;
        auVar77 = ZEXT816(0);
        while( true ) {
          if ((int)lVar42 < (int)uVar35) {
            lVar42 = (long)(int)lVar42;
            while (*(char *)(lVar27 + lVar42) != '\0') {
              lVar42 = lVar42 + 1;
              if (lVar46 == lVar42) goto LAB_1b709af84;
            }
          }
          uVar32 = (uint)lVar42;
          if (uVar32 == uVar35) break;
          lVar30 = (long)(int)uVar32 + (long)(int)uVar32 * 2;
          lVar43 = (long)(int)lVar30 * 4;
          lVar39 = (long)*(int *)(lVar26 + lVar43);
          lVar41 = (long)*(int *)(lVar26 + lVar30 * 4 + 4);
          lVar30 = (long)*(int *)(lVar26 + lVar43 + 8);
          if (*(char *)(lVar54 + lVar39) == '\0') {
            uVar31 = *(ulong *)(lVar45 + lVar39 * 8);
            iVar85 = (int)uVar31 >> 1;
            iVar98 = (int)((long)uVar31 >> 0x21);
            iVar101 = -(int)(uVar31 & 0x100000001);
            iVar86 = -(int)((uVar31 & 0x100000001) >> 0x20);
            iVar101 = CONCAT13((char)(uVar31 >> 0x18) >> 1 ^ (byte)((uint)iVar101 >> 0x18),
                               CONCAT12((byte)((uint)iVar85 >> 0x10) ^ (byte)((uint)iVar101 >> 0x10)
                                        ,CONCAT11((byte)((uint)iVar85 >> 8) ^
                                                  (byte)((uint)iVar101 >> 8),
                                                  (byte)iVar85 ^ (byte)iVar101)));
            *(ulong *)(lVar20 + lVar39 * 8) =
                 CONCAT44((int)(CONCAT17((byte)((long)uVar31 >> 0x39) ^ (byte)((uint)iVar86 >> 0x18)
                                         ,CONCAT16((byte)((uint)iVar98 >> 0x10) ^
                                                   (byte)((uint)iVar86 >> 0x10),
                                                   CONCAT15((byte)((uint)iVar98 >> 8) ^
                                                            (byte)((uint)iVar86 >> 8),
                                                            CONCAT14((byte)iVar98 ^ (byte)iVar86,
                                                                     iVar101)))) >> 0x20) +
                          auVar77._4_4_,iVar101 + auVar77._0_4_);
            *(undefined1 *)(lVar54 + lVar39) = 1;
            if (*(char *)(lVar54 + lVar41) == '\0') goto LAB_1b709af1c;
LAB_1b709ad04:
            cVar15 = *(char *)(lVar54 + lVar30);
          }
          else {
            if (*(char *)(lVar54 + lVar41) != '\0') goto LAB_1b709ad04;
LAB_1b709af1c:
            auVar77._0_8_ = *(ulong *)(lVar20 + lVar39 * 8);
            auVar77._8_8_ = 0;
            uVar31 = *(ulong *)(lVar45 + lVar41 * 8);
            iVar85 = (int)uVar31 >> 1;
            iVar98 = (int)((long)uVar31 >> 0x21);
            iVar101 = -(int)(uVar31 & 0x100000001);
            iVar86 = -(int)((uVar31 & 0x100000001) >> 0x20);
            iVar101 = CONCAT13((char)(uVar31 >> 0x18) >> 1 ^ (byte)((uint)iVar101 >> 0x18),
                               CONCAT12((byte)((uint)iVar85 >> 0x10) ^ (byte)((uint)iVar101 >> 0x10)
                                        ,CONCAT11((byte)((uint)iVar85 >> 8) ^
                                                  (byte)((uint)iVar101 >> 8),
                                                  (byte)iVar85 ^ (byte)iVar101)));
            *(ulong *)(lVar20 + lVar41 * 8) =
                 CONCAT44((int)(CONCAT17((byte)((long)uVar31 >> 0x39) ^ (byte)((uint)iVar86 >> 0x18)
                                         ,CONCAT16((byte)((uint)iVar98 >> 0x10) ^
                                                   (byte)((uint)iVar86 >> 0x10),
                                                   CONCAT15((byte)((uint)iVar98 >> 8) ^
                                                            (byte)((uint)iVar86 >> 8),
                                                            CONCAT14((byte)iVar98 ^ (byte)iVar86,
                                                                     iVar101)))) >> 0x20) +
                          (int)(auVar77._0_8_ >> 0x20),iVar101 + (int)auVar77._0_8_);
            *(undefined1 *)(lVar54 + lVar41) = 1;
            cVar15 = *(char *)(lVar54 + lVar30);
          }
          if (cVar15 == '\0') {
            uVar29 = *(undefined8 *)(lVar20 + lVar39 * 8);
            uVar88 = *(undefined8 *)(lVar20 + lVar41 * 8);
            iVar101 = CONCAT13(~(byte)((ulong)uVar29 >> 0x18),
                               CONCAT12(~(byte)((ulong)uVar29 >> 0x10),
                                        CONCAT11(~(byte)((ulong)uVar29 >> 8),~(byte)uVar29)));
            iVar86 = (int)uVar88 - iVar101;
            auVar77._0_4_ = iVar86 / 2;
            auVar77._4_4_ =
                 ((int)((ulong)uVar88 >> 0x20) -
                 (int)(CONCAT17(~(byte)((ulong)uVar29 >> 0x38),
                                CONCAT16(~(byte)((ulong)uVar29 >> 0x30),
                                         CONCAT15(~(byte)((ulong)uVar29 >> 0x28),
                                                  CONCAT14(~(byte)((ulong)uVar29 >> 0x20),iVar101)))
                               ) >> 0x20)) / 2;
            auVar77._8_8_ = 0;
            uVar31 = *(ulong *)(lVar45 + lVar30 * 8);
            iVar98 = (int)uVar31 >> 1;
            iVar100 = (int)((long)uVar31 >> 0x21);
            iVar101 = -(int)(uVar31 & 0x100000001);
            iVar85 = -(int)((uVar31 & 0x100000001) >> 0x20);
            iVar101 = CONCAT13((char)(uVar31 >> 0x18) >> 1 ^ (byte)((uint)iVar101 >> 0x18),
                               CONCAT12((byte)((uint)iVar98 >> 0x10) ^ (byte)((uint)iVar101 >> 0x10)
                                        ,CONCAT11((byte)((uint)iVar98 >> 8) ^
                                                  (byte)((uint)iVar101 >> 8),
                                                  (byte)iVar98 ^ (byte)iVar101)));
            *(ulong *)(lVar20 + lVar30 * 8) =
                 CONCAT44((int)(CONCAT17((byte)((long)uVar31 >> 0x39) ^ (byte)((uint)iVar85 >> 0x18)
                                         ,CONCAT16((byte)((uint)iVar100 >> 0x10) ^
                                                   (byte)((uint)iVar85 >> 0x10),
                                                   CONCAT15((byte)((uint)iVar100 >> 8) ^
                                                            (byte)((uint)iVar85 >> 8),
                                                            CONCAT14((byte)iVar100 ^ (byte)iVar85,
                                                                     iVar101)))) >> 0x20) +
                          auVar77._4_4_,iVar101 + iVar86 / 2);
            *(undefined1 *)(lVar54 + lVar30) = 1;
          }
          lVar30 = 0;
          *puVar25 = uVar32;
          iVar101 = 1;
          *(undefined1 *)(lVar27 + (int)uVar32) = 1;
          do {
            lVar39 = (long)(int)puVar25[lVar30];
            uVar31 = lVar39 * 3;
            iVar86 = *(int *)(lVar23 + lVar39 * 0xc);
            if (iVar86 != -1) {
              lVar41 = (long)*(int *)(lVar26 + (long)iVar86 * 4);
              if (*(char *)(lVar54 + lVar41) == '\0') {
                uVar49 = -(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 | (uVar31 & 0xffffffff) << 2;
                uVar29 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + uVar49 + 4) * 8);
                uVar88 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + uVar49 + 8) * 8);
                uVar89 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + lVar39 * 0xc) * 8);
                auVar77._0_4_ = ((int)uVar88 + (int)uVar29) - (int)uVar89;
                auVar77._4_4_ =
                     ((int)((ulong)uVar88 >> 0x20) + (int)((ulong)uVar29 >> 0x20)) -
                     (int)((ulong)uVar89 >> 0x20);
                auVar77._8_8_ = 0;
                uVar49 = *(ulong *)(lVar45 + lVar41 * 8);
                iVar100 = (int)uVar49 >> 1;
                iVar103 = (int)((long)uVar49 >> 0x21);
                iVar85 = -(int)(uVar49 & 0x100000001);
                iVar98 = -(int)((uVar49 & 0x100000001) >> 0x20);
                iVar85 = CONCAT13((char)(uVar49 >> 0x18) >> 1 ^ (byte)((uint)iVar85 >> 0x18),
                                  CONCAT12((byte)((uint)iVar100 >> 0x10) ^
                                           (byte)((uint)iVar85 >> 0x10),
                                           CONCAT11((byte)((uint)iVar100 >> 8) ^
                                                    (byte)((uint)iVar85 >> 8),
                                                    (byte)iVar100 ^ (byte)iVar85)));
                *(ulong *)(lVar20 + lVar41 * 8) =
                     CONCAT44((int)(CONCAT17((byte)((long)uVar49 >> 0x39) ^
                                             (byte)((uint)iVar98 >> 0x18),
                                             CONCAT16((byte)((uint)iVar103 >> 0x10) ^
                                                      (byte)((uint)iVar98 >> 0x10),
                                                      CONCAT15((byte)((uint)iVar103 >> 8) ^
                                                               (byte)((uint)iVar98 >> 8),
                                                               CONCAT14((byte)iVar103 ^ (byte)iVar98
                                                                        ,iVar85)))) >> 0x20) +
                              auVar77._4_4_,iVar85 + auVar77._0_4_);
                *(undefined1 *)(lVar54 + lVar41) = 1;
              }
              uVar32 = iVar86 / 3;
              if (*(char *)(lVar27 + (int)uVar32) == '\0') {
                puVar25[iVar101] = uVar32;
                iVar101 = iVar101 + 1;
                *(undefined1 *)(lVar27 + (int)uVar32) = 1;
              }
            }
            iVar86 = *(int *)(lVar23 + (uVar31 + 1) * 4);
            if (iVar86 != -1) {
              lVar41 = (long)*(int *)(lVar26 + (long)iVar86 * 4);
              if (*(char *)(lVar54 + lVar41) == '\0') {
                uVar29 = *(undefined8 *)
                          (lVar20 + (long)*(int *)(lVar26 + (-(uVar31 >> 0x1f & 1) &
                                                             0xfffffffc00000000 |
                                                            (uVar31 & 0xffffffff) << 2) + 8) * 8);
                uVar88 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + lVar39 * 0xc) * 8);
                uVar89 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + (uVar31 + 1) * 4) * 8);
                auVar77._0_4_ = ((int)uVar88 + (int)uVar29) - (int)uVar89;
                auVar77._4_4_ =
                     ((int)((ulong)uVar88 >> 0x20) + (int)((ulong)uVar29 >> 0x20)) -
                     (int)((ulong)uVar89 >> 0x20);
                auVar77._8_8_ = 0;
                uVar49 = *(ulong *)(lVar45 + lVar41 * 8);
                iVar100 = (int)uVar49 >> 1;
                iVar103 = (int)((long)uVar49 >> 0x21);
                iVar85 = -(int)(uVar49 & 0x100000001);
                iVar98 = -(int)((uVar49 & 0x100000001) >> 0x20);
                iVar85 = CONCAT13((char)(uVar49 >> 0x18) >> 1 ^ (byte)((uint)iVar85 >> 0x18),
                                  CONCAT12((byte)((uint)iVar100 >> 0x10) ^
                                           (byte)((uint)iVar85 >> 0x10),
                                           CONCAT11((byte)((uint)iVar100 >> 8) ^
                                                    (byte)((uint)iVar85 >> 8),
                                                    (byte)iVar100 ^ (byte)iVar85)));
                *(ulong *)(lVar20 + lVar41 * 8) =
                     CONCAT44((int)(CONCAT17((byte)((long)uVar49 >> 0x39) ^
                                             (byte)((uint)iVar98 >> 0x18),
                                             CONCAT16((byte)((uint)iVar103 >> 0x10) ^
                                                      (byte)((uint)iVar98 >> 0x10),
                                                      CONCAT15((byte)((uint)iVar103 >> 8) ^
                                                               (byte)((uint)iVar98 >> 8),
                                                               CONCAT14((byte)iVar103 ^ (byte)iVar98
                                                                        ,iVar85)))) >> 0x20) +
                              auVar77._4_4_,iVar85 + auVar77._0_4_);
                *(undefined1 *)(lVar54 + lVar41) = 1;
              }
              uVar32 = iVar86 / 3;
              if (*(char *)(lVar27 + (int)uVar32) == '\0') {
                puVar25[iVar101] = uVar32;
                iVar101 = iVar101 + 1;
                *(undefined1 *)(lVar27 + (int)uVar32) = 1;
              }
            }
            iVar86 = *(int *)(lVar23 + (uVar31 + 2) * 4);
            if (iVar86 != -1) {
              lVar41 = (long)*(int *)(lVar26 + (long)iVar86 * 4);
              if (*(char *)(lVar54 + lVar41) == '\0') {
                uVar29 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + lVar39 * 0xc) * 8);
                uVar88 = *(undefined8 *)
                          (lVar20 + (long)*(int *)(lVar26 + (-(uVar31 >> 0x1f & 1) &
                                                             0xfffffffc00000000 |
                                                            (uVar31 & 0xffffffff) << 2) + 4) * 8);
                uVar89 = *(undefined8 *)(lVar20 + (long)*(int *)(lVar26 + (uVar31 + 2) * 4) * 8);
                auVar77._0_4_ = ((int)uVar88 + (int)uVar29) - (int)uVar89;
                auVar77._4_4_ =
                     ((int)((ulong)uVar88 >> 0x20) + (int)((ulong)uVar29 >> 0x20)) -
                     (int)((ulong)uVar89 >> 0x20);
                auVar77._8_8_ = 0;
                uVar31 = *(ulong *)(lVar45 + lVar41 * 8);
                iVar100 = (int)uVar31 >> 1;
                iVar103 = (int)((long)uVar31 >> 0x21);
                iVar85 = -(int)(uVar31 & 0x100000001);
                iVar98 = -(int)((uVar31 & 0x100000001) >> 0x20);
                iVar85 = CONCAT13((char)(uVar31 >> 0x18) >> 1 ^ (byte)((uint)iVar85 >> 0x18),
                                  CONCAT12((byte)((uint)iVar100 >> 0x10) ^
                                           (byte)((uint)iVar85 >> 0x10),
                                           CONCAT11((byte)((uint)iVar100 >> 8) ^
                                                    (byte)((uint)iVar85 >> 8),
                                                    (byte)iVar100 ^ (byte)iVar85)));
                *(ulong *)(lVar20 + lVar41 * 8) =
                     CONCAT44((int)(CONCAT17((byte)((long)uVar31 >> 0x39) ^
                                             (byte)((uint)iVar98 >> 0x18),
                                             CONCAT16((byte)((uint)iVar103 >> 0x10) ^
                                                      (byte)((uint)iVar98 >> 0x10),
                                                      CONCAT15((byte)((uint)iVar103 >> 8) ^
                                                               (byte)((uint)iVar98 >> 8),
                                                               CONCAT14((byte)iVar103 ^ (byte)iVar98
                                                                        ,iVar85)))) >> 0x20) +
                              auVar77._4_4_,iVar85 + auVar77._0_4_);
                *(undefined1 *)(lVar54 + lVar41) = 1;
              }
              uVar32 = iVar86 / 3;
              if (*(char *)(lVar27 + (int)uVar32) == '\0') {
                puVar25[iVar101] = uVar32;
                iVar101 = iVar101 + 1;
                *(undefined1 *)(lVar27 + (int)uVar32) = 1;
              }
            }
            lVar30 = lVar30 + 1;
          } while (lVar30 < iVar101);
        }
LAB_1b709af84:
        if (0 < (int)uVar33) {
          if (uVar33 < 4) {
            uVar31 = 0;
          }
          else {
            lVar42 = 0;
            uVar31 = uVar37 & 0x7ffffffc;
            uVar49 = uVar31;
            do {
              pauVar10 = (undefined1 (*) [16])(lVar20 + lVar42 * 8);
              auVar78 = NEON_scvtf(*pauVar10,4);
              auVar68 = NEON_scvtf(pauVar10[1],4);
              auVar70._0_8_ = CONCAT44(auVar68._4_4_ * fVar72,auVar68._0_4_ * fVar72);
              auVar70._8_4_ = auVar68._8_4_ * fVar72;
              auVar70._12_4_ = auVar68._12_4_ * fVar72;
              auVar79._0_8_ = CONCAT44(auVar78._4_4_ * fVar72,auVar78._0_4_ * fVar72);
              auVar79._8_4_ = auVar78._8_4_ * fVar72;
              auVar79._12_4_ = auVar78._12_4_ * fVar72;
              *(long *)(*pauVar10 + 8) = auVar79._8_8_;
              *(undefined8 *)*pauVar10 = auVar79._0_8_;
              *(long *)(pauVar10[1] + 8) = auVar70._8_8_;
              *(undefined8 *)pauVar10[1] = auVar70._0_8_;
              lVar42 = lVar42 + 4;
              uVar49 = uVar49 - 4;
            } while (uVar49 != 0);
            if (uVar31 == uVar37) goto LAB_1b709b380;
          }
          lVar42 = uVar37 - uVar31;
          do {
            uVar29 = NEON_scvtf(*(undefined8 *)(lVar20 + uVar31 * 8),4);
            *(ulong *)(lVar20 + uVar31 * 8) =
                 CONCAT44((float)((ulong)uVar29 >> 0x20) * fVar72,(float)uVar29 * fVar72);
            uVar31 = uVar31 + 1;
            lVar42 = lVar42 + -1;
          } while (lVar42 != 0);
        }
      }
LAB_1b709b380:
      func_0x0001b81206e0(puVar25);
      func_0x0001b81206e0(lVar27);
      func_0x0001b81206e0(lVar54);
      func_0x0001b81206e0(lVar45);
      func_0x0001b81206e0(lVar23);
      param_15[4] = (long)((long)pfVar51 + (-param_15[4] - (long)param_1));
LAB_1b709b3d4:
      pfVar44 = pfVar51;
      if ((2 < (int)fVar63) && (uStack_100 == 0)) {
        if (uStack_230 == 0) {
          uStack_100 = 2;
        }
        else {
          lVar20 = 0;
          bVar13 = *(byte *)pfVar51;
          uVar37 = (ulong)bVar13 & 0x3f;
          bVar18 = (bVar13 & 0x40) == 0;
          uVar31 = 6;
          pfVar44 = (float *)((long)pfVar51 + 1);
          uVar33 = 1;
          do {
            lVar45 = uStack_230 + lVar20;
            if (bVar18) {
              uVar31 = -uVar37;
              if (-1 < (char)bVar13) {
                uVar31 = uVar37;
              }
              if (uVar31 == 0) {
                uStack_100 = 0;
                goto LAB_1b7099b68;
              }
              param_15[5] = (long)pfVar44 - (long)param_1;
              uVar33 = *param_4;
              lVar42 = *param_9;
              uVar35 = *param_13;
              uVar32 = uVar35 * 3;
              lVar23 = func_0x0001b8120b80(-(ulong)(uVar32 >> 0x1f) & 0xfffffffc00000000 |
                                           (ulong)uVar32 << 2,0x100004052888210);
              *param_11 = lVar23;
              if (lVar45 != 1) {
                lVar46 = 0;
                bVar13 = *(byte *)pfVar44;
                uVar37 = lVar45 - 2;
                uVar49 = (ulong)bVar13 & 0x3f;
                bVar18 = (bVar13 & 0x40) == 0;
                uVar31 = 6;
                pfStack_268 = (float *)((long)pfVar44 + 1);
                uVar36 = 1;
                goto LAB_1b709b524;
              }
              uStack_238 = 0;
              uVar31 = 0;
              goto LAB_1b709b8c4;
            }
            if (lVar45 == 1) {
              uStack_100 = 2;
              pfVar44 = (float *)((long)pfVar51 + uStack_230);
              goto LAB_1b7099b68;
            }
            pfVar53 = (float *)((long)pfVar44 + 1);
            bVar14 = *(byte *)pfVar44;
            pfVar44 = pfVar53;
            if (((int)lVar20 == -8) && ((bVar14 & 0x7c) != 0)) break;
            bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
            uVar37 = ((ulong)bVar14 & 0x7f) << (uVar31 & 0x3f) | uVar37;
            uVar31 = uVar31 + 7;
            lVar20 = lVar20 + -1;
            uVar35 = uVar33 + 1;
            bVar19 = uVar33 < 9;
            uVar33 = uVar35;
          } while ((bVar19) || (-1 < (char)bVar14));
          uStack_100 = 2;
        }
      }
      goto LAB_1b7099b68;
    }
    uVar34 = 0;
    uVar49 = 1;
  }
  else {
    uVar34 = uVar49 + 1;
    do {
      uVar49 = uVar49 - 1;
      bVar13 = *(byte *)(lVar20 + uVar49);
      *(byte *)(lVar20 + ((uVar49 & 0x3fffffffffffffff) << 1 | 1)) = bVar13 >> 4;
      *(byte *)(lVar20 + uVar49 * 2) = bVar13 & 0xf;
      uVar34 = uVar34 - 1;
    } while (1 < uVar34);
    uVar49 = uVar37;
    if (uVar35 < 8) {
      uVar34 = 0;
    }
    else {
      if (uVar35 < 0x20) {
        uVar40 = 0;
      }
      else {
        lVar54 = 0;
        uVar34 = uVar37 & 0x7fffffe0;
        uVar40 = uVar34;
        do {
          pcVar9 = (char *)(lVar20 + lVar54);
          auVar69._0_8_ =
               CONCAT17(pcVar9[7] * '\x02',
                        CONCAT16(pcVar9[6] * '\x02',
                                 CONCAT15(pcVar9[5] * '\x02',
                                          CONCAT14(pcVar9[4] * '\x02',
                                                   CONCAT13(pcVar9[3] * '\x02',
                                                            CONCAT12(pcVar9[2] * '\x02',
                                                                     CONCAT11(pcVar9[1] * '\x02',
                                                                              *pcVar9 * '\x02'))))))
                       );
          auVar69[8] = pcVar9[8] * '\x02';
          auVar69[9] = pcVar9[9] * '\x02';
          auVar69[10] = pcVar9[10] * '\x02';
          auVar69[0xb] = pcVar9[0xb] * '\x02';
          auVar69[0xc] = pcVar9[0xc] * '\x02';
          auVar69[0xd] = pcVar9[0xd] * '\x02';
          auVar69[0xe] = pcVar9[0xe] * '\x02';
          auVar69[0xf] = pcVar9[0xf] * '\x02';
          auVar76._0_8_ =
               CONCAT17(pcVar9[0x17] * '\x02',
                        CONCAT16(pcVar9[0x16] * '\x02',
                                 CONCAT15(pcVar9[0x15] * '\x02',
                                          CONCAT14(pcVar9[0x14] * '\x02',
                                                   CONCAT13(pcVar9[0x13] * '\x02',
                                                            CONCAT12(pcVar9[0x12] * '\x02',
                                                                     CONCAT11(pcVar9[0x11] * '\x02',
                                                                              pcVar9[0x10] * '\x02')
                                                                    ))))));
          auVar76[8] = pcVar9[0x18] * '\x02';
          auVar76[9] = pcVar9[0x19] * '\x02';
          auVar76[10] = pcVar9[0x1a] * '\x02';
          auVar76[0xb] = pcVar9[0x1b] * '\x02';
          auVar76[0xc] = pcVar9[0x1c] * '\x02';
          auVar76[0xd] = pcVar9[0x1d] * '\x02';
          auVar76[0xe] = pcVar9[0x1e] * '\x02';
          auVar76[0xf] = pcVar9[0x1f] * '\x02';
          *(long *)(pcVar9 + 8) = auVar69._8_8_;
          *(undefined8 *)pcVar9 = auVar69._0_8_;
          *(long *)(pcVar9 + 0x18) = auVar76._8_8_;
          *(undefined8 *)(pcVar9 + 0x10) = auVar76._0_8_;
          lVar54 = lVar54 + 0x20;
          uVar40 = uVar40 - 0x20;
        } while (uVar40 != 0);
        if (uVar34 == uVar37) goto LAB_1b709a8a4;
        uVar40 = uVar34;
        if ((uVar37 & 0x18) == 0) goto LAB_1b709a888;
      }
      uVar34 = uVar37 & 0x7ffffff8;
      lVar54 = uVar40 - uVar34;
      do {
        uVar29 = *(undefined8 *)(lVar20 + uVar40);
        *(ulong *)(lVar20 + uVar40) =
             CONCAT17((char)((ulong)uVar29 >> 0x38) * '\x02',
                      CONCAT16((char)((ulong)uVar29 >> 0x30) * '\x02',
                               CONCAT15((char)((ulong)uVar29 >> 0x28) * '\x02',
                                        CONCAT14((char)((ulong)uVar29 >> 0x20) * '\x02',
                                                 CONCAT13((char)((ulong)uVar29 >> 0x18) * '\x02',
                                                          CONCAT12((char)((ulong)uVar29 >> 0x10) *
                                                                   '\x02',CONCAT11((char)((ulong)
                                                  uVar29 >> 8) * '\x02',(char)uVar29 * '\x02')))))))
        ;
        uVar40 = uVar40 + 8;
        lVar54 = lVar54 + 8;
      } while (lVar54 != 0);
      if (uVar34 == uVar37) goto LAB_1b709a8a4;
    }
  }
LAB_1b709a888:
  lVar54 = uVar49 - uVar34;
  do {
    *(char *)(lVar20 + uVar34) = *(char *)(lVar20 + uVar34) << 1;
    uVar34 = uVar34 + 1;
    lVar54 = lVar54 + -1;
  } while (lVar54 != 0);
LAB_1b709a8a4:
  func_0x0001b8120bd0(lVar42,0xff,uVar31);
  func_0x0001b8120bd0(lVar45,0xff,lVar26);
  uVar31 = 0;
  uVar33 = 0;
  iVar101 = 0;
  do {
    uVar49 = (ulong)(int)uVar31;
    uVar34 = uVar37;
    if ((long)uVar37 < (long)(uVar49 + 1)) {
      uVar34 = uVar49 + 1;
    }
LAB_1b709a904:
    uVar31 = uVar49;
    if ((*(byte *)(lVar20 + uVar31) & 1) != 0) break;
    uVar32 = 0;
    *(byte *)(lVar20 + uVar31) = *(byte *)(lVar20 + uVar31) | 1;
    *puVar28 = (int)uVar31;
    uVar12 = *(undefined4 *)(lVar30 + (long)iVar101 * 4);
    iVar86 = 1;
    do {
      iVar85 = iVar86 + -1;
      iVar98 = puVar28[iVar85];
      lVar39 = (long)iVar98;
      *(undefined4 *)(lVar46 + lVar39 * 4) = uVar12;
      iVar98 = iVar98 * 3;
      iVar100 = *(int *)(lVar48 + (long)iVar98 * 4);
      lVar26 = (long)iVar98;
      lVar54 = (long)*(int *)(lVar27 + (long)iVar98 * 4);
      iVar98 = *(int *)(lVar45 + lVar54 * 4);
      if (iVar98 == -1) {
        *(uint *)(lVar45 + lVar54 * 4) = uVar33;
        iVar98 = *(int *)(lVar27 + lVar26 * 4);
        *(int *)(lVar23 + (long)(int)uVar32 * 4) = iVar98;
        uVar33 = uVar33 + 1;
        uVar32 = uVar32 + 1;
        iVar98 = *(int *)(lVar45 + (long)iVar98 * 4);
      }
      *(int *)(lVar42 + lVar26 * 4) = iVar98;
      if (iVar100 != -1) {
        if ((*(byte *)(lVar20 + lVar39) >> 1 & 1) == 0) {
          iVar98 = iVar100 / 3;
          bVar13 = *(byte *)(lVar20 + iVar98);
          if ((bVar13 & 1) == 0) {
            *(byte *)(lVar20 + iVar98) = bVar13 | 1;
            puVar28[iVar85] = iVar98;
            iVar85 = iVar86;
          }
        }
        *(undefined4 *)(lVar48 + lVar26 * 4) = 0xffffffff;
        *(undefined4 *)(lVar48 + (long)iVar100 * 4) = 0xffffffff;
      }
      lVar54 = lVar26 + 1;
      iVar98 = *(int *)(lVar48 + lVar54 * 4);
      lVar41 = (long)*(int *)(lVar27 + lVar54 * 4);
      iVar86 = *(int *)(lVar45 + lVar41 * 4);
      if (iVar86 == -1) {
        *(uint *)(lVar45 + lVar41 * 4) = uVar33;
        iVar86 = *(int *)(lVar27 + lVar54 * 4);
        *(int *)(lVar23 + (long)(int)uVar32 * 4) = iVar86;
        uVar33 = uVar33 + 1;
        uVar32 = uVar32 + 1;
        iVar86 = *(int *)(lVar45 + (long)iVar86 * 4);
      }
      *(int *)(lVar42 + lVar54 * 4) = iVar86;
      iVar86 = iVar85;
      if (iVar98 != -1) {
        if ((*(byte *)(lVar20 + lVar39) >> 2 & 1) == 0) {
          iVar86 = iVar98 / 3;
          bVar13 = *(byte *)(lVar20 + iVar86);
          if ((bVar13 & 1) == 0) {
            *(byte *)(lVar20 + iVar86) = bVar13 | 1;
            puVar28[iVar85] = iVar86;
            iVar85 = iVar85 + 1;
          }
        }
        *(undefined4 *)(lVar48 + lVar54 * 4) = 0xffffffff;
        *(undefined4 *)(lVar48 + (long)iVar98 * 4) = 0xffffffff;
        iVar86 = iVar85;
      }
      lVar26 = lVar26 + 2;
      iVar98 = *(int *)(lVar48 + lVar26 * 4);
      lVar54 = (long)*(int *)(lVar27 + lVar26 * 4);
      iVar85 = *(int *)(lVar45 + lVar54 * 4);
      if (iVar85 == -1) {
        *(uint *)(lVar45 + lVar54 * 4) = uVar33;
        iVar85 = *(int *)(lVar27 + lVar26 * 4);
        *(int *)(lVar23 + (long)(int)uVar32 * 4) = iVar85;
        uVar33 = uVar33 + 1;
        uVar32 = uVar32 + 1;
        iVar85 = *(int *)(lVar45 + (long)iVar85 * 4);
      }
      *(int *)(lVar42 + lVar26 * 4) = iVar85;
      if (iVar98 != -1) {
        if ((*(byte *)(lVar20 + lVar39) >> 3 & 1) == 0) {
          iVar85 = iVar98 / 3;
          bVar13 = *(byte *)(lVar20 + iVar85);
          if ((bVar13 & 1) == 0) {
            *(byte *)(lVar20 + iVar85) = bVar13 | 1;
            puVar28[iVar86] = iVar85;
            iVar86 = iVar86 + 1;
          }
        }
        *(undefined4 *)(lVar48 + lVar26 * 4) = 0xffffffff;
        *(undefined4 *)(lVar48 + (long)iVar98 * 4) = 0xffffffff;
      }
    } while (iVar86 != 0);
    iVar101 = iVar101 + 1;
    if (0 < (int)uVar32) {
      lVar26 = 0;
      uVar49 = (ulong)uVar32;
      do {
        *(undefined4 *)(lVar45 + (long)*(int *)(lVar23 + lVar26 * 4) * 4) = 0xffffffff;
        lVar26 = lVar26 + 1;
        uVar49 = uVar49 - 1;
      } while (uVar49 != 0);
    }
LAB_1b709a8ec:
    if ((int)uVar35 <= (int)uVar31) goto LAB_1b709a420;
  } while( true );
  uVar49 = uVar31 + 1;
  uVar31 = uVar34;
  if (uVar34 == uVar49) goto LAB_1b709a8ec;
  goto LAB_1b709a904;
  while( true ) {
    pfVar44 = (float *)((long)pfVar51 + uStack_230);
    if (lVar26 == 0) goto LAB_1b709b8b4;
    pfVar53 = (float *)((long)pfStack_268 + 1);
    bVar14 = *(byte *)pfStack_268;
    uVar37 = uVar37 - 1;
    if (((int)lVar46 == -8) && ((bVar14 & 0x7c) != 0)) {
      uStack_238 = 0;
      uVar31 = 0;
      lVar45 = 0;
      uStack_100 = 0x10;
      goto LAB_1b709b8c8;
    }
    bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
    uVar49 = ((ulong)bVar14 & 0x7f) << (uVar31 & 0x3f) | uVar49;
    uVar31 = uVar31 + 7;
    lVar46 = lVar46 + -1;
    uVar2 = uVar36 + 1;
    bVar19 = 8 < uVar36;
    pfStack_268 = pfVar53;
    uVar36 = uVar2;
    if ((bVar19) && ((char)bVar14 < 0)) break;
LAB_1b709b524:
    lVar45 = uStack_230 + lVar20 + lVar46;
    lVar26 = lVar45 + -2;
    if (bVar18) {
      iVar101 = -(int)uVar49;
      if (-1 < (char)bVar13) {
        iVar101 = (int)uVar49;
      }
      if (0 < iVar101) {
        uStack_238 = 0;
        lStack_270 = 0;
        uStack_100 = 0x80000000;
        goto LAB_1b709c0f0;
      }
      pfVar44 = pfStack_268;
      if (lVar26 == 0) goto LAB_1b709b8b4;
      bVar13 = *(byte *)pfStack_268;
      uVar37 = lVar45 - 3;
      uVar34 = (ulong)bVar13 & 0x3f;
      bVar18 = (bVar13 & 0x40) == 0;
      pfVar44 = (float *)((long)pfStack_268 + lVar26);
      uVar31 = 6;
      pfVar53 = (float *)((long)pfStack_268 + 1);
      uVar49 = (uStack_230 + lVar20 + lVar46) - 5;
      uVar36 = 1;
      goto LAB_1b709b840;
    }
  }
  uStack_238 = 0;
  uVar31 = 0;
  lVar45 = 0;
  uStack_100 = 0x10;
  uVar37 = (uStack_230 + lVar20 + lVar46) - 2;
  goto LAB_1b709b8c8;
  while( true ) {
    if (uVar40 == 0xfffffffffffffffe) goto LAB_1b709b8b4;
    pfVar51 = (float *)((long)pfVar53 + 1);
    bVar14 = *(byte *)pfVar53;
    uVar37 = uVar37 - 1;
    pfVar53 = pfVar51;
    if ((uVar36 == 9) && ((bVar14 & 0x7c) != 0)) goto LAB_1b709c1e4;
    bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
    uVar34 = ((ulong)bVar14 & 0x7f) << (uVar31 & 0x3f) | uVar34;
    uVar31 = uVar31 + 7;
    uVar2 = uVar36 + 1;
    bVar19 = 8 < uVar36;
    uVar49 = uVar40 - 1;
    uVar36 = uVar2;
    if ((bVar19) && ((char)bVar14 < 0)) break;
LAB_1b709b840:
    uVar40 = uVar49;
    if (bVar18) {
      uVar31 = -uVar34;
      if (-1 < (char)bVar13) {
        uVar31 = uVar34;
      }
      uStack_238 = (uint)uVar31;
      if (uVar40 + 2 != 0) {
        bVar13 = *(byte *)pfVar53;
        uVar37 = uVar40 + 1;
        uVar34 = (ulong)bVar13 & 0x3f;
        bVar18 = (bVar13 & 0x40) == 0;
        pfVar44 = (float *)((long)pfVar53 + uVar40 + 2);
        uVar49 = 6;
        uStack_100 = 0x10;
        pfVar53 = (float *)((long)pfVar53 + 1);
        uVar36 = 1;
        goto LAB_1b709c174;
      }
      uVar37 = 0;
      lVar45 = 0;
      uStack_100 = 2;
      goto LAB_1b709b8c8;
    }
  }
  uVar37 = uVar40 + 1;
LAB_1b709c1e4:
  uStack_238 = 0;
  lVar45 = 0;
  uVar31 = 0;
  uStack_100 = 0x10;
  goto LAB_1b709b8c8;
LAB_1b709b8b4:
  uStack_238 = 0;
  uVar31 = 0;
LAB_1b709b8c4:
  lVar45 = 0;
  uStack_100 = 2;
  pfVar53 = pfVar44;
  uVar37 = 0;
  goto LAB_1b709b8c8;
  while( true ) {
    if (uVar40 == 0xffffffffffffffff) goto LAB_1b709b8c4;
    pfVar51 = (float *)((long)pfVar53 + 1);
    bVar14 = *(byte *)pfVar53;
    pfVar53 = pfVar51;
    if ((uVar36 == 9) && ((bVar14 & 0x7c) != 0)) {
      lVar45 = 0;
      uStack_100 = 0x10;
      uVar37 = uVar40;
      goto LAB_1b709b8c8;
    }
    bVar18 = (uint)(int)(char)bVar14 < 0x80000000;
    uVar34 = ((ulong)bVar14 & 0x7f) << (uVar49 & 0x3f) | uVar34;
    uVar49 = uVar49 + 7;
    uVar40 = uVar40 - 1;
    uVar37 = uVar37 - 1;
    uVar2 = uVar36 + 1;
    bVar19 = 8 < uVar36;
    uVar36 = uVar2;
    if ((bVar19) && ((char)bVar14 < 0)) break;
LAB_1b709c174:
    if (bVar18) {
      uStack_100 = 0;
      uVar37 = uVar40 + 1;
      iVar101 = -(int)uVar34;
      if (-1 < (char)bVar13) {
        iVar101 = (int)uVar34;
      }
      lVar45 = (long)iVar101;
      goto LAB_1b709b8c8;
    }
  }
  lVar45 = 0;
LAB_1b709b8c8:
  lStack_270 = func_0x0001b8120b80(-(uVar31 >> 0x1f & 1) & 0xfffffffc00000000 |
                                   (uVar31 & 0xffffffff) << 2,0x100004052888210);
  lVar20 = func_0x0001b8120b70(lVar45,1,0x100004077774924);
  pfStack_268 = pfVar53;
  if (((uVar31 & 0xffffffff) == 0) || (uStack_100 != 0)) {
joined_r0x0001b709ba0c:
    if ((lVar45 != 0) && (uStack_100 == 0)) {
      uStack_8c = 0;
      uStack_90 = 0;
      if (uVar37 == 0) goto LAB_1b709bb64;
      pfVar51 = (float *)((long)pfStack_268 + 1);
      bVar13 = *(byte *)pfStack_268;
      if (bVar13 == 0xff) {
        uVar31 = uVar37 - 9;
        if (uVar37 < 9) goto LAB_1b709bb74;
        uVar49 = (ulong)*(byte *)((long)pfStack_268 + 1);
        uVar37 = (ulong)*(uint7 *)((long)pfStack_268 + 2);
        pfStack_268 = (float *)((long)pfStack_268 + 9);
      }
      else {
        iVar101 = 7;
        if ((bVar13 & 0x40) != 0) {
          iVar101 = 8;
        }
        iVar86 = 6;
        if ((bVar13 & 0x20) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 5;
        if ((bVar13 & 0x10) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 4;
        if ((bVar13 & 8) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 3;
        if ((bVar13 & 4) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 2;
        if ((bVar13 & 2) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 1;
        if ((bVar13 & 1) != 0) {
          iVar101 = iVar86;
        }
        uVar49 = (ulong)(iVar101 - 1);
        uVar31 = (uVar37 - 1) - uVar49;
        if (uVar37 - 1 < uVar49) {
LAB_1b709bb74:
          uStack_100 = 2;
          pfStack_268 = pfVar51;
          goto LAB_1b709bc0c;
        }
        func_0x0001b8120bb0(&uStack_90,pfVar51,uVar49);
        pfStack_268 = (float *)((long)pfVar51 + uVar49);
        uVar49 = ((ulong)uStack_90 << 8 | (ulong)uStack_8c << 0x28 | (ulong)bVar13) >> iVar101;
        uVar37 = uVar49 >> 8;
      }
      uVar37 = uVar49 & 0xff | uVar37 << 8;
      if ((lVar20 == 0) || (lVar46 = byet(pfStack_268,uVar37,lVar20,lVar45,1), lVar46 == lVar45)) {
        uVar49 = 0;
        if (uVar37 <= uVar31) {
          uVar49 = uVar37;
        }
        uStack_100 = 2;
        if (uVar37 <= uVar31) {
          uStack_100 = 0;
        }
        pfStack_268 = (float *)((long)pfStack_268 + uVar49);
      }
      else {
LAB_1b709bc08:
        uStack_100 = 0x80000000;
      }
    }
  }
  else {
    auStack_94._0_3_ = 0;
    uStack_98 = 0;
    if (uVar37 == 0) {
LAB_1b709badc:
      auStack_94._0_3_ = 0;
      uStack_100 = 2;
      uStack_98 = 0;
    }
    else {
      pfStack_268 = (float *)((long)pfVar53 + 1);
      bVar13 = *(byte *)pfVar53;
      if ((ulong)bVar13 == 0xff) {
        uStack_1a0 = uVar37 - 9;
        if (8 < uVar37) {
          uStack_98 = *(uint *)((long)pfVar53 + 2);
          uVar49 = (ulong)*(byte *)((long)pfVar53 + 1);
          uVar37 = (ulong)*(uint7 *)((long)pfVar53 + 2);
          auStack_94[2] = *(byte *)(pfVar53 + 2);
          auStack_94._0_2_ = (short)*(undefined3 *)((long)pfVar53 + 6);
          pfStack_268 = (float *)((long)pfVar53 + 9);
          goto LAB_1b709bb2c;
        }
      }
      else {
        iVar101 = 7;
        if ((bVar13 & 0x40) != 0) {
          iVar101 = 8;
        }
        iVar86 = 6;
        if ((bVar13 & 0x20) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 5;
        if ((bVar13 & 0x10) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 4;
        if ((bVar13 & 8) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 3;
        if ((bVar13 & 4) != 0) {
          iVar101 = iVar86;
        }
        iVar86 = 2;
        if ((bVar13 & 2) != 0) {
          iVar86 = iVar101;
        }
        iVar101 = 1;
        if ((bVar13 & 1) != 0) {
          iVar101 = iVar86;
        }
        uVar49 = (ulong)(iVar101 - 1);
        uStack_1a0 = (uVar37 - 1) - uVar49;
        if (uVar37 - 1 < uVar49) goto LAB_1b709badc;
        func_0x0001b8120bb0(&uStack_98,pfStack_268,uVar49);
        pfStack_268 = (float *)((long)pfStack_268 + uVar49);
        uVar49 = ((ulong)uStack_98 << 8 | (ulong)(uint3)auStack_94._0_3_ << 0x28 | (ulong)bVar13) >>
                 iVar101;
        uVar37 = uVar49 >> 8;
        uStack_98 = (uint)(uVar49 >> 8);
        auStack_94._0_3_ = (undefined3)(uVar49 >> 0x28);
LAB_1b709bb2c:
        uVar49 = uVar49 & 0xff | uVar37 << 8;
        if ((lStack_270 != 0) &&
           (lVar46 = byet(pfStack_268,uVar49,lStack_270,(long)(int)uVar31,4), lVar46 != (int)uVar31)
           ) goto LAB_1b709bc08;
        uVar37 = uStack_1a0 - uVar49;
        if (uVar49 <= uStack_1a0) {
          uStack_100 = 0;
          pfStack_268 = (float *)((long)pfStack_268 + uVar49);
          goto joined_r0x0001b709ba0c;
        }
      }
LAB_1b709bb64:
      uStack_100 = 2;
    }
  }
LAB_1b709bc0c:
  lVar45 = func_0x0001b8120b80((long)(int)uVar32 << 3,0x100004000313f17);
  func_0x0001b8120bd0(lVar45,0xff,(long)(int)uVar32 << 3);
  if (uStack_100 == 0) {
    if ((int)uVar35 < 1) {
      uStack_238 = 0;
    }
    else {
      uVar31 = 0;
      uVar32 = 0;
      uStack_238 = 0;
      iVar101 = 0;
      uVar37 = (ulong)uVar33;
      do {
        uVar49 = (ulong)uVar32;
        lVar46 = (long)*(int *)(lVar42 + (ulong)uVar32 * 4);
        puVar25 = (uint *)(lVar45 + lVar46 * 8);
        uVar33 = *puVar25;
        if (uVar33 == 0xffffffff) {
          *puVar25 = uStack_238;
          *(uint *)(lVar23 + uVar49 * 4) = uStack_238;
          uStack_238 = uStack_238 + 1;
        }
        else {
          bVar13 = *(byte *)(lVar20 + iVar101);
          iVar86 = bVar13 - 1;
          lVar26 = lVar46;
          if (iVar86 != 0) {
            do {
              iVar85 = *(int *)(lVar45 + lVar26 * 8 + 4);
              lVar46 = (long)iVar85;
              if (iVar85 == -1) goto LAB_1b709bd40;
              iVar86 = iVar86 + -1;
              lVar26 = lVar46;
            } while (iVar86 != 0);
            uVar33 = *(uint *)(lVar45 + lVar46 * 8);
          }
          *(uint *)(lVar23 + uVar49 * 4) = uVar33;
          bVar13 = *(byte *)(lVar20 + iVar101);
          lVar26 = lVar46;
LAB_1b709bd40:
          if (bVar13 == 0) {
            *(int *)(lVar45 + lVar26 * 8 + 4) = (int)uVar37;
            uVar34 = uVar37 << 3;
            uVar40 = uVar37 >> 0x1f;
            uVar37 = (ulong)((int)uVar37 + 1);
            *(uint *)(lVar45 + (-uVar40 & 0xfffffff800000000 | uVar34)) = uStack_238;
            *(uint *)(lVar23 + uVar49 * 4) = uStack_238;
            uStack_238 = uStack_238 + 1;
          }
          iVar101 = iVar101 + 1;
        }
        uVar31 = uVar31 + 1;
        uVar34 = uVar49 + 1;
        if (uVar34 < uVar31 * 3) {
          lVar46 = (long)*(int *)(lVar42 + uVar34 * 4);
          puVar25 = (uint *)(lVar45 + lVar46 * 8);
          uVar33 = *puVar25;
          if (uVar33 == 0xffffffff) {
            *puVar25 = uStack_238;
            *(uint *)(lVar23 + uVar34 * 4) = uStack_238;
            uStack_238 = uStack_238 + 1;
          }
          else {
            bVar13 = *(byte *)(lVar20 + iVar101);
            iVar86 = bVar13 - 1;
            lVar26 = lVar46;
            if (iVar86 != 0) {
              do {
                iVar85 = *(int *)(lVar45 + lVar26 * 8 + 4);
                lVar46 = (long)iVar85;
                if (iVar85 == -1) goto LAB_1b709bde8;
                iVar86 = iVar86 + -1;
                lVar26 = lVar46;
              } while (iVar86 != 0);
              uVar33 = *(uint *)(lVar45 + lVar46 * 8);
            }
            *(uint *)(lVar23 + uVar34 * 4) = uVar33;
            bVar13 = *(byte *)(lVar20 + iVar101);
            lVar26 = lVar46;
LAB_1b709bde8:
            uVar40 = uVar37;
            if (bVar13 == 0) {
              uVar40 = (ulong)((int)uVar37 + 1);
              *(int *)(lVar45 + lVar26 * 8 + 4) = (int)uVar37;
              *(uint *)(lVar45 + (-(uVar37 >> 0x1f) & 0xfffffff800000000 | uVar37 << 3)) =
                   uStack_238;
              *(uint *)(lVar23 + uVar34 * 4) = uStack_238;
              uStack_238 = uStack_238 + 1;
            }
            iVar101 = iVar101 + 1;
            uVar37 = uVar40;
          }
          lVar46 = uVar49 + 2;
          lVar26 = (long)*(int *)(lVar42 + lVar46 * 4);
          puVar25 = (uint *)(lVar45 + lVar26 * 8);
          uVar33 = *puVar25;
          if (uVar33 == 0xffffffff) {
            *puVar25 = uStack_238;
            *(uint *)(lVar23 + lVar46 * 4) = uStack_238;
            uStack_238 = uStack_238 + 1;
          }
          else {
            bVar13 = *(byte *)(lVar20 + iVar101);
            iVar86 = bVar13 - 1;
            lVar27 = lVar26;
            if (iVar86 != 0) {
              do {
                iVar85 = *(int *)(lVar45 + lVar27 * 8 + 4);
                lVar26 = (long)iVar85;
                if (iVar85 == -1) goto LAB_1b709be80;
                iVar86 = iVar86 + -1;
                lVar27 = lVar26;
              } while (iVar86 != 0);
              uVar33 = *(uint *)(lVar45 + lVar26 * 8);
            }
            *(uint *)(lVar23 + lVar46 * 4) = uVar33;
            bVar13 = *(byte *)(lVar20 + iVar101);
            lVar27 = lVar26;
LAB_1b709be80:
            uVar49 = uVar37;
            if (bVar13 == 0) {
              uVar49 = (ulong)((int)uVar37 + 1);
              *(int *)(lVar45 + lVar27 * 8 + 4) = (int)uVar37;
              *(uint *)(lVar45 + (-(uVar37 >> 0x1f) & 0xfffffff800000000 | uVar37 << 3)) =
                   uStack_238;
              *(uint *)(lVar23 + lVar46 * 4) = uStack_238;
              uStack_238 = uStack_238 + 1;
            }
            iVar101 = iVar101 + 1;
            uVar37 = uVar49;
          }
        }
        uVar32 = uVar32 + 3;
      } while (uVar31 != uVar35);
    }
  }
  func_0x0001b81206e0(lVar45);
  func_0x0001b81206e0(lVar20);
  if (uStack_100 == 0) {
    lVar20 = func_0x0001b8120b80((long)(int)uStack_238 * 0xc,0x10000403e1c8ba9);
    *param_7 = lVar20;
    if (0 < (int)uStack_238) {
      uVar31 = (ulong)uStack_238;
      if (uStack_238 < 4) {
        uVar37 = 0;
      }
      else {
        lVar45 = 0;
        uVar37 = uVar31 & 0x7ffffffc;
        uVar49 = uVar37;
        do {
          pfVar51 = (float *)(lVar20 + lVar45 * 0xc);
          pauVar8 = (undefined1 (*) [12])(lStack_270 + lVar45 * 4);
          auVar93 = *pauVar8;
          uVar33 = *(uint *)pauVar8[1];
          auVar71._0_4_ = *(uint *)*pauVar8 >> 0x10;
          auVar71._4_4_ = *(uint *)(*pauVar8 + 4) >> 0x10;
          auVar71._8_4_ = *(uint *)(*pauVar8 + 8) >> 0x10;
          auVar71._12_4_ = uVar33 >> 0x10;
          auVar68 = NEON_ucvtf(auVar71,4);
          fVar72 = fVar55;
          fVar56 = (float)func_0x0001b811fab0();
          auVar16._4_4_ = auVar68._4_4_ * fVar55;
          auVar16._0_4_ = auVar68._0_4_ * fVar55;
          auVar16._8_4_ = auVar68._8_4_ * fVar55;
          auVar16._12_4_ = auVar68._12_4_ * fVar55;
          fVar64 = fVar72;
          func_0x0001b811fab0(auVar16);
          fVar63 = fVar64;
          fVar57 = (float)func_0x0001b811fab0();
          auVar80._4_4_ = fVar56;
          auVar80._0_4_ = extraout_s0;
          auVar80._8_4_ = fVar57;
          auVar80._12_4_ = extraout_var;
          fVar58 = (float)func_0x0001b811fab0();
          auVar81._2_2_ = 0;
          auVar81._0_2_ = auVar93._0_2_;
          auVar81[4] = auVar93[4];
          auVar81[5] = auVar93[5];
          auVar81._6_2_ = 0;
          auVar81[8] = auVar93[8];
          auVar81[9] = auVar93[9];
          auVar81._10_2_ = 0;
          auVar81[0xc] = (char)uVar33;
          auVar81[0xd] = (char)(uVar33 >> 8);
          auVar81._14_2_ = 0;
          auVar68 = NEON_ucvtf(auVar81,4);
          auVar82._8_4_ = 0xc0490fdb;
          auVar82._0_8_ = 0xc0490fdbc0490fdb;
          auVar82._12_4_ = 0xc0490fdb;
          fVar59 = (float)func_0x0001b811fab0();
          fStack_190 = auVar82._0_4_;
          auVar17._4_4_ =
               (auVar68._4_4_ * fVar55) /
               (float)((uint)fVar56 ^ ((uint)fVar56 ^ 0x358637bd) & -(uint)(fVar56 < 1e-06)) +
               -3.1415927;
          auVar17._0_4_ =
               (auVar68._0_4_ * fVar55) /
               (float)((uint)extraout_s0 ^
                      ((uint)extraout_s0 ^ 0x358637bd) & -(uint)(extraout_s0 < 1e-06)) + -3.1415927;
          auVar17._8_4_ =
               (auVar68._8_4_ * fVar55) /
               (float)((uint)fVar57 ^ ((uint)fVar57 ^ 0x358637bd) & -(uint)(fVar57 < 1e-06)) +
               -3.1415927;
          auVar17._12_4_ =
               (auVar68._12_4_ * fVar55) /
               (float)((uint)fVar58 ^ ((uint)fVar58 ^ 0x358637bd) & -(uint)(fVar58 < 1e-06)) +
               -3.1415927;
          fVar60 = (float)func_0x0001b811fab0(auVar17);
          auVar83._8_8_ = auVar82._8_8_;
          auVar83._0_4_ = auVar82._0_4_;
          auVar83._4_4_ = fStack_190;
          auVar68 = auVar83;
          fVar61 = (float)func_0x0001b811fab0();
          fVar73 = auVar68._0_4_;
          fVar62 = (float)func_0x0001b811fab0();
          *pfVar51 = auVar83._0_4_ * extraout_s0;
          pfVar51[1] = fVar60 * extraout_s0;
          pfVar51[2] = fVar64;
          pfVar51[3] = fStack_190 * fVar56;
          pfVar51[4] = fVar59 * fVar56;
          pfVar51[5] = fVar72;
          pfVar51[6] = fVar73 * fVar57;
          pfVar51[7] = fVar61 * fVar57;
          pfVar51[8] = fVar63;
          pfVar51[9] = auVar68._0_4_ * fVar58;
          pfVar51[10] = fVar62 * fVar58;
          pfVar51[0xb] = auVar80._0_4_;
          lVar45 = lVar45 + 4;
          uVar49 = uVar49 - 4;
        } while (uVar49 != 0);
        if (uVar37 == uVar31) goto LAB_1b709c0e8;
      }
      lVar45 = uVar31 - uVar37;
      do {
        pfVar51 = (float *)(lVar20 + uVar37 * 0xc);
        uVar33 = *(uint *)(lStack_270 + uVar37 * 4);
        auVar84._8_8_ = 0;
        auVar84._0_8_ = uVar65;
        fVar63 = (float)func_0x0001b811fab0();
        auVar68 = ZEXT416((uint)(fVar55 * (float)(uVar33 & 0xffff)));
        fVar64 = (float)func_0x0001b811fab0();
        *pfVar51 = auVar68._0_4_ * fVar63;
        pfVar51[1] = fVar64 * fVar63;
        pfVar51[2] = auVar84._0_4_;
        uVar37 = uVar37 + 1;
        lVar45 = lVar45 + -1;
      } while (lVar45 != 0);
    }
LAB_1b709c0e8:
    uStack_100 = 0;
  }
LAB_1b709c0f0:
  func_0x0001b81206e0(lStack_270);
  *param_8 = uStack_238;
  param_15[5] = (long)((long)pfStack_268 + (-param_15[5] - (long)param_1));
  pfVar44 = pfStack_268;
LAB_1b7099b68:
  func_0x0001b81206e0(lVar48);
  if ((uStack_100 == 0) && ((long)pfVar44 - (long)param_1 == param_2)) {
    uVar29 = 0;
  }
  else {
    func_0x0001b81206e0(*param_3);
    func_0x0001b81206e0(*param_5);
    func_0x0001b81206e0(*param_7);
    func_0x0001b81206e0(*param_9);
    func_0x0001b81206e0(*param_10);
    func_0x0001b81206e0(*param_12);
    func_0x0001b81206e0(*param_11);
    func_0x0001b81206e0(*param_14);
    *param_3 = 0;
    *param_5 = 0;
    *param_7 = 0;
    *param_11 = 0;
    *param_12 = 0;
    *param_10 = 0;
    *param_9 = 0;
    *param_8 = 0;
    *param_13 = 0;
    *param_6 = 0;
    *param_4 = 0;
    uVar29 = 0xffffffffffffffff;
    *param_14 = 0;
  }
  return uVar29;
}

