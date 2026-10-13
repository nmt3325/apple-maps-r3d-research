
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Possible PIC construction at 0x0001b70ae20c: Changing call to branch */
/* WARNING: Removing unreachable block (ram,0x0001b70ae210) */

void reorder_faces(long param_1,long param_2,uint param_3)

{
  int iVar1;
  code *pcVar2;
  ulong uVar3;
  long lVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  ulong uVar8;
  int iVar9;
  ulong uVar10;
  long lVar11;
  long lVar12;
  ulong uVar13;
  long lVar14;
  long lVar15;
  ulong unaff_x30;
  undefined8 uVar16;
  undefined8 uVar17;
  
  lVar12 = *(long *)(param_1 + 0x60);
  uVar3 = -(ulong)(param_3 * 3 >> 0x1f) & 0xfffffffc00000000 | (ulong)(param_3 * 3) << 2;
  lVar4 = func_0x0001b8120b80(uVar3,0x100004052888210);
  lVar15 = *(long *)(param_1 + 0xa8);
  lVar14 = *(long *)(param_1 + 0x90);
  lVar7 = lVar14 + 1;
  lVar6 = *(long *)(param_1 + 0xb8);
  if (lVar6 <= lVar14) {
    lVar11 = 0x40;
    if (lVar6 != 0) {
      lVar11 = lVar6 << 1;
    }
    if (lVar11 <= lVar7) {
      lVar11 = lVar7;
    }
    if (lVar11 != 0) {
      uVar5 = func_0x0001b8120b90(*(undefined8 *)(param_1 + 0xb0),lVar11 << 2,0x100004052888210);
      *(undefined8 *)(param_1 + 0xb0) = uVar5;
    }
    *(long *)(param_1 + 0xb8) = lVar11;
  }
  if (lVar15 <= lVar14) {
    func_0x0001b811fc60(*(long *)(param_1 + 0xb0) + *(long *)(param_1 + 0xa8) * 4,
                        (lVar7 - lVar15) * 4);
  }
  lVar7 = *(long *)(param_1 + 0x90);
  *(long *)(param_1 + 0xa8) = lVar7 + 1;
  uVar13 = (ulong)param_3;
  if (0 < (int)param_3) {
    lVar6 = 0;
    lVar14 = *(long *)(param_1 + 0xb0);
    uVar8 = uVar13;
    do {
      lVar15 = (long)*(int *)(param_2 + lVar6 * 4) * 4 + 4;
      *(int *)(lVar14 + lVar15) = *(int *)(lVar14 + lVar15) + 1;
      lVar6 = lVar6 + 1;
      uVar8 = uVar8 - 1;
    } while (uVar8 != 0);
  }
  if (0 < lVar7) {
    iVar9 = 0;
    lVar14 = *(long *)(param_1 + 0xb0);
    lVar6 = 1;
    do {
      iVar1 = *(int *)(lVar14 + lVar6 * 4);
      *(int *)(lVar14 + lVar6 * 4) = iVar9;
      iVar9 = iVar1 + iVar9;
      lVar6 = lVar6 + 1;
      lVar7 = lVar7 + -1;
    } while (lVar7 != 0);
  }
  if ((int)param_3 < 1) {
    lVar7 = *(long *)(param_1 + 0x50);
  }
  else {
    lVar6 = 0;
    lVar14 = *(long *)(param_1 + 0xb0);
    lVar7 = *(long *)(param_1 + 0x50);
    uVar8 = uVar13;
    do {
      iVar9 = *(int *)(lVar14 + (long)*(int *)(param_2 + lVar6 * 4) * 4 + 4);
      lVar11 = lVar6 * 0xc;
      *(undefined4 *)(lVar4 + (long)iVar9 * 0xc) = *(undefined4 *)(lVar7 + lVar11);
      lVar15 = (long)(iVar9 * 3) * 4;
      *(undefined4 *)(lVar4 + lVar15 + 4) = *(undefined4 *)(lVar7 + lVar11 + 4);
      *(undefined4 *)(lVar4 + lVar15 + 8) = *(undefined4 *)(lVar7 + lVar11 + 8);
      lVar15 = (long)*(int *)(param_2 + lVar6 * 4) * 4 + 4;
      *(int *)(lVar14 + lVar15) = *(int *)(lVar14 + lVar15) + 1;
      lVar6 = lVar6 + 1;
      uVar8 = uVar8 - 1;
    } while (uVar8 != 0);
  }
  func_0x0001b8120bb0(lVar7,lVar4,uVar3);
  if (lVar12 < 1) {
    if (((unaff_x30 ^ unaff_x30 << 1) >> 0x3e & 1) == 0) {
      halt_baddata();
    }
                    /* WARNING: Does not return */
    pcVar2 = (code *)SoftwareBreakpoint(0xc471,0x1b70ae204);
    (*pcVar2)();
  }
  uVar3 = *(ulong *)(param_1 + 0x90);
  if (0 < (int)uVar3) {
    lVar7 = *(long *)(param_1 + 0xb0);
    uVar8 = uVar3 & 0x7fffffff;
    if (7 < uVar8) {
      lVar6 = 0;
      uVar10 = uVar3 & 0x7ffffff8;
      do {
        lVar12 = lVar7 + (uVar8 - lVar6) * 4 + -4;
        uVar5 = *(undefined8 *)(lVar12 + -0xc);
        uVar17 = *(undefined8 *)(lVar12 + -0x14);
        uVar16 = *(undefined8 *)(lVar12 + -0x1c);
        lVar14 = lVar7 + (uVar8 - lVar6) * 4;
        *(undefined8 *)(lVar14 + -4) = *(undefined8 *)(lVar12 + -4);
        *(undefined8 *)(lVar14 + -0xc) = uVar5;
        *(undefined8 *)(lVar14 + -0x14) = uVar17;
        *(undefined8 *)(lVar14 + -0x1c) = uVar16;
        lVar6 = lVar6 + 8;
        uVar10 = uVar10 - 8;
      } while (uVar10 != 0);
      if (uVar8 == (uVar3 & 0x7ffffff8)) goto LAB_1b70ae148;
      uVar8 = uVar3 & 7;
    }
    uVar10 = uVar8 - 1;
    *(undefined4 *)(lVar7 + uVar8 * 4) = *(undefined4 *)(lVar7 + uVar10 * 4);
    uVar3 = uVar8 - 2;
    if ((1 < uVar8) &&
       (*(undefined4 *)(lVar7 + uVar10 * 4) = *(undefined4 *)(lVar7 + uVar3 * 4), 1 < uVar10)) {
      uVar10 = uVar8 - 3;
      *(undefined4 *)(lVar7 + uVar3 * 4) = *(undefined4 *)(lVar7 + uVar10 * 4);
      if (1 < uVar3) {
        uVar3 = uVar8 - 4;
        *(undefined4 *)(lVar7 + uVar10 * 4) = *(undefined4 *)(lVar7 + uVar3 * 4);
        if (1 < uVar10) {
          uVar10 = uVar8 - 5;
          *(undefined4 *)(lVar7 + uVar3 * 4) = *(undefined4 *)(lVar7 + uVar10 * 4);
          if (1 < uVar3) {
            *(undefined4 *)(lVar7 + uVar10 * 4) = *(undefined4 *)(lVar7 + (uVar8 - 6) * 4);
            if (1 < uVar10) {
              *(undefined4 *)(lVar7 + (uVar8 - 6) * 4) = *(undefined4 *)(lVar7 + uVar8 * 4 + -0x1c);
            }
          }
        }
      }
    }
  }
LAB_1b70ae148:
  if (0 < (int)param_3) {
    lVar7 = 0;
    lVar12 = *(long *)(param_1 + 0xb0);
    lVar6 = *(long *)(param_1 + 0x68);
    do {
      iVar9 = *(int *)(lVar12 + (long)*(int *)(param_2 + lVar7 * 4) * 4 + 4);
      lVar15 = lVar7 * 0xc;
      *(undefined4 *)(lVar4 + (long)iVar9 * 0xc) = *(undefined4 *)(lVar6 + lVar15);
      lVar14 = (long)(iVar9 * 3) * 4;
      *(undefined4 *)(lVar4 + lVar14 + 4) = *(undefined4 *)(lVar6 + lVar15 + 4);
      *(undefined4 *)(lVar4 + lVar14 + 8) = *(undefined4 *)(lVar6 + lVar15 + 8);
      lVar14 = (long)*(int *)(param_2 + lVar7 * 4) * 4 + 4;
      *(int *)(lVar12 + lVar14) = *(int *)(lVar12 + lVar14) + 1;
      lVar7 = lVar7 + 1;
      uVar13 = uVar13 - 1;
    } while (uVar13 != 0);
  }
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

