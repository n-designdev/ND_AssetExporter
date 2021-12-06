
if __name__ == '__main__':
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode")
    import ndPyLibExportAnim
    reload(ndPyLibExportAnim)
    argsdic = {'shot': 'c001', 'sequence': 's646', 'export_type': 'anim',
    'env_load': 'True', 'Priority': 'u50', 'Group': 'u128gb', 'stepValue': '1.0',
    'namespace': 'NursedesseiDirtDragon',
    'bake_anim': 'True', 'scene_timeworp': 'True',
    # 'animOutput': 'P:/Project/RAM1/shots/ep006/s646/c001/publish/test_charSet/NursedesseiShip/v003/anim/NursedesseiShip.ma',
    'animOutput': 'C:/Users/k_ueda/Desktop/work/NursedesseiDragon',
     'framerange_output': 'True',
     'input_path': 'P:/Project/RAM1/shots/ep006/s646/c001/work/k_ueda/test.ma', 'Pool': 'uram1',
    #  'assetpath': 'P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiShip/publish/Setup/RH/maya/current/NursedesseiShip_Rig_RH.mb',
     'assetpath': 'P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiDirtDragon/publish/Model/RH/maya/current/NursedesseiDirtDragon_Mdl_RH.mb', 
      'framerange': 'None', 'chara': 'NursedesseiDirtDragon', 'topnode': 'root', 'framehundle': '0', 'project': 'RAM1',
     'testmode': 'True',
    #   'output': 'P:/Project/RAM1/shots/ep006/s646/c001/publish/test_charSet/NursedesseiShip/v003/anim',
      'output': 'C:/Users/k_ueda/Desktop/work',
    #   'export_item': 'ctrl_set, root,ctrloffA_set, *ik*,*LOC*, *JNT*, leg_L_grp, leg_R_grp, *fk*,ctrl_allWorld_parentConstraint1, AllRoot'}
    #   'export_item': 'ctrl_set, root,ctrloffA}
    #   'export_item': 'ctrl_set, root,ctrloffA, *LOC*, *JNT*, leg_L_grp, leg_R_grp, *ctrl*'}
      'export_item': 'ctrl_set, root,ctrloffA'}
    ndPyLibExportAnim.ndPyLibExportAnim_caller(argsdic)