#####################################################################################
# copies LION dataset from Bytes Production Version Folder to Production SDE (accompanied by metadata)
# USER NEEDS TO SUPPLY VERSION PARAMETER TO BE ARCHIVED ex 15A and new VERSION from M drive ex "15C" "15D"
# meta_export function utilizes arcpy.ExportMetadata_conversion to export metadata as .xml from Production SDE to appropriate M Drive layer folder


import arcpy, os, datetime, sys, traceback, ConfigParser
arcpy.env.overwriteOutput = True

try:
    
    # Disconnect SDE users to remove locks during FC transfer
    def disconnect_disable_sde(TrueOrFalse, sde_path):
        arcpy.env.workspace = sde_path
        arcpy.env.overwriteOutput = True
        if TrueOrFalse.lower() == 'true':
            print("Disconnecting users and blocking sde access until transfer is complete")
            arcpy.AcceptConnections(sde_path, False)
            arcpy.DisconnectUser(sde_path, "ALL")
        else:
            print("Ignoring user/sde disconnect")


    def meta_export(sde_src, output_dir, output_name):
        arcpy.ExportMetadata_conversion(sde_src, translator, os.path.join(output_dir, output_name))

    # Log file
    # Set configuration file for defining path and credential information
    print('Parsing configuration file')
    root_path = os.path.dirname(os.path.abspath(__file__))
    ini_path = os.path.join(root_path, 'LION_Districts.ini')
    config = ConfigParser.ConfigParser()
    config.read(ini_path)
    
    log_path = config.get('PATHS', 'log_path')
    log = open(log_path, "a")
    StartTime = datetime.datetime.now().replace(microsecond = 0)
    date = datetime.datetime.today().strftime("%Y%m%d")
    log.write(str(StartTime) + "\t")

    version = config.get('LION_DISTRICTS_VARS', 'version')
    disconnect = config.get('LION_DISTRICTS_VARS', 'toggle_disconnect')
    sde = config.get('LION_DISTRICTS_VARS', 'sde_path')
    toggle_lion = config.get('LION_DISTRICTS_VARS', 'toggle_lion')
    toggle_districts = config.get('LION_DISTRICTS_VARS', 'toggle_districts')
    m_lion_path = config.get('PATHS', 'lion_path')
    m_bytes_lion_path = config.get('PATHS', 'bytes_lion_path')
    m_census_path = config.get('PATHS', 'census_path')
    m_bytes_census_path = config.get('PATHS', 'bytes_census_path')
    m_bytes_bb_cd_path = config.get('PATHS', 'bytes_bb_cd_path')
    m_bytes_pol_admin_path = config.get('PATHS', 'bytes_pol_admin_path')
    m_bytes_school_fire_health_path = config.get('PATHS', 'bytes_school_fire_health_path')
    m_bytes_other_path = config.get('PATHS', 'bytes_other_path')
    m_bound_pol_path = config.get('PATHS', 'political_path')
    m_bound_school_path = config.get('PATHS', 'school_path')
    m_bound_munic_path = config.get('PATHS', 'municipal_path')
    m_bound_borough_path = config.get('PATHS', 'borough_path')
    lion_dir_1 = config.get('PATHS', 'lion_dir_1')
    lion_dir_2 = config.get('PATHS', 'lion_dir_2')
    districts_dir_1 = config.get('PATHS', 'districts_dir_1')
    districts_dir_2 = config.get('PATHS', 'districts_dir_2')

    # Set path to translation file used for metadata transfer
    Arcdir = arcpy.GetInstallInfo("desktop")["InstallDir"]
    translator = Arcdir + "Metadata/Translator/ARCGIS2FGDC.xml"


    disconnect_disable_sde(disconnect, sde)
    
    #############################################################################################
    
    ## START OF COPY NEW DATA TO GISPROD
    ###############################################################################################
    # Copies M drive GIS output to sde.PROD
    # 2 different .gdb's get copied to sde.PROD (lion.gdb and Districts.gdb)
    # overwrite output must be TRUE, do not need arcpy.Delete_management

    ###connect to prod sde
    arcpy.env.workspace = sde
    new_outFolder = sde
    print ("Start of copy M drive " + str(version) + " to PROD")

    if toggle_lion.lower() == 'true':

        #set workspace to lion.gdb
        arcpy.env.workspace = os.path.join(lion_dir_1, version, lion_dir_2)

        arcpy.env.overwriteOutput = True

        # FC's in M drive lion.gdb that are copied to PROD
        newLION = ["lion", "node"]

        for new in newLION:
            #print new
            print ("Copying: " + str(arcpy.env.workspace) + "\\" + str(new))
            if new == "lion":
                # output location
                newLION_outFC = os.path.join(new_outFolder, new.upper())
                print ("new_outFC = " + str(newLION_outFC))

                #arcpy.FeatureClassToFeatureClass_conversion(new, new_outFolder, "LION_TEST")
                arcpy.CopyFeatures_management(new, newLION_outFC)
                
                lion_meta_list = ['LION - Generic.lyr.xml', 'LION - Roadbeds.lyr.xml',
                                  'LION - Street Name Labels.lyr.xml', 'LION Streets - Generic.lyr.xml',
                                  'LION Streets - Roadbeds.lyr.xml']
                for lyr in lion_meta_list:
                    meta_export(newLION_outFC, m_lion_path, lyr)
                    meta_export(newLION_outFC, m_bytes_lion_path, lyr)
                #arcpy.TruncateTable_management(newLION_outFC)
                #arcpy.Append_management(new, newLION_outFC)
                log.write("" + newLION_outFC + "\n")
                print ("---------")

            else:

                # output location
                newLION_outFC = os.path.join(new_outFolder, "LION_" + new)
                print ("new_outFC = " + str(newLION_outFC))

                #arcpy.FeatureClassToFeatureClass_conversion(new, new_outFolder, "LION_node")
                arcpy.CopyFeatures_management(new, newLION_outFC)
                node_meta_list = ['LION - Nodes.lyr.xml']
                for lyr in node_meta_list:
                    meta_export(newLION_outFC, m_lion_path, lyr)
                    meta_export(newLION_outFC, m_bytes_lion_path, lyr)
                #arcpy.TruncateTable_management(newLION_outFC)
                #arcpy.Append_management(new, newLION_outFC)
                log.write("" + newLION_outFC + "\n")
                print ("---------")

    else:
        print("LION toggle set to False. If you meant to run LION change toggle_lion variable in LION_Districts.ini")

    # set newDistricts .gdb 

    if toggle_districts.lower() == 'true':

        #set workspace to districts.gdb
        arcpy.env.workspace = os.path.join(districts_dir_1, version, districts_dir_2)

        arcpy.env.overwriteOutput = True

        # FC's in M drive Districts.gdb that are copied to PROD
        newDISTRICTS = ["nyad","nyadwi","nyap","nybb","nybbwi","nycb2020",
                      "nycb2020wi","nycb2010","nycb2010wi","nycc","nyccwi","nycd", "nycdta2020",
                      "nycdwi","nycg","nycgwi","nyct2020","nyct2020wi","nyct2010","nyct2010wi",
                      "nyed","nyedwi","nyfb","nyfc","nyfd","nyha","nyhc","nyhez",
                      "nymc","nymcwi","nynta2020","nynta2010","nypp","nysd","nyss","nysswi", "nypuma2010"]

        district_name_dict = {
            "nyad": "NYAD - New York State Assembly Districts.lyr.xml",
            "nyadwi": "NYADWI - New York State Assembly Districts - Water Included.lyr.xml",
            "nyap": "NYAP - Atomic Polygons.lyr.xml",
            "nybb": "NYBB - Borough Boundaries.lyr.xml",
            "nybbwi": "NYBBWI - Borough Boundaries - Water Included.lyr.xml",
            "nycb2020": "NYCB2020 - 2020 Census Blocks.lyr.xml",
            "nycb2020wi": "NYCB2020WI - 2020 Census Blocks - Water Included.lyr.xml",
            "nycb2010": "NYCB2010 - 2010 Census Blocks.lyr.xml",
            "nycb2010wi": "NYCB2010WI - 2010 Census Blocks - Water Included.lyr.xml",
            "nycc": "NYCC - City Council Districts.lyr.xml",
            "nyccwi": "NYCCWI - City Council Districts - Water Included.lyr.xml",
            "nycd": "NYCD - Community Districts.lyr.xml",
            "nycdta2020": "NYCDTA2020 - 2020 Community District Tabulation Areas.lyr.xml",
            "nycdwi": "NYCDWI - Community Districts - Water Included.lyr.xml",
            "nycg": "NYCG - Congressional Districts.lyr.xml",
            "nycgwi": "NYCGWI - Congressional Districts - Water Included.lyr.xml",
            "nyct2020": "NYCT2020 - 2020 Census Tracts.lyr.xml",
            "nyct2020wi": "NYCT2020WI - 2020 Census Tracts - Water Included.lyr.xml",
            "nyct2010": "NYCT2010 - 2010 Census Tracts.lyr.xml",
            "nyct2010wi": "NYCT2010WI - 2010 Census Tracts - Water Included.lyr.xml",
            "nyed": "NYED - Election Districts.lyr.xml",
            "nyedwi": "NYEDWI - Election Districts - Water Included.lyr.xml",
            "nyfb": "NYFB - Fire Battalions.lyr.xml",
            "nyfc": "NYFC - Fire Companies.lyr.xml",
            "nyfd": "NYFD - Fire Divisions.lyr.xml",
            "nyha": "NYHA - Health Areas.lyr.xml",
            "nyhc": "NYHC - Health Center Districts.lyr.xml",
            "nyhez": "NYHEZ - Hurricane Evacuation Zones.lyr.xml",
            "nymc": "NYMC - Municipal Court Districts.lyr.xml",
            "nymcwi": "NYMCWI - Municipal Court Districts - Water Included.lyr.xml",
            "nynta2020": "NYNTA2020 - 2020 Neighborhood Tabulation Areas.lyr.xml",
            "nynta2010": "NYNTA2010 - 2010 Neighborhood Tabulation Areas.lyr.xml",
            "nypp": "NYPP - Police Precints.lyr.xml",
            "nypuma2010": "NYPUMA2010 - 2010 Public Use Micro Areas (PUMAs).lyr.xml",
            "nysd": "NYSD - School Districts.lyr.xml",
            "nyss": "NYSS - New York State Senate Districts.lyr.xml",
            "nysswi": "NYSSWI - New York State Senate Districts - Water Included.lyr.xml"}

        #the below lists are utilized to distribute xmls to the appropriate M Drive subfolders
        bb_cd = ['nybb', 'nybbwi', 'nycd', 'nycdwi']
        census = ['nycb2020', 'nycb2020wi', 'nycb2010', 'nycb2010wi', 'nycdta2020', 'nynta2010', 'nynta2020',
                  'nypuma2010', 'nyct2020', 'nyct2020wi', 'nyct2010', 'nyct2010wi']
        other = ['nyap', 'nyhez']
        pol = ['nyad', 'nyadwi', 'nycc', 'nyccwi', 'nycg', 'nycgwi', 'nyed', 'nyedwi', 'nymc', 'nymcwi', 'nyss', 'nysswi']
        fire = ['nyfb', 'nyfc', 'nyfd', 'nyha', 'nyhc', 'nypp', 'nysd']
        #Boundaries sub folders (minus census)
        bound_munic = ['nyfb', 'nyfc', 'nyfd', 'nyha', 'nyhc', 'nypp', 'nyhez'] 
        bound_school = ['nysd']
        bound_borough = ['nybb', 'nybbwi']
        bound_pol = ['nyad', 'nyadwi', 'nycc', 'nyccwi', 'nycg', 'nycgwi', 'nyed', 'nyedwi', 'nyss', 'nysswi', 'nymc', 'nymcwi', 'nycd', 'nycdwi'] 
        
        for FC in newDISTRICTS:
            #print FC
            print ("Copying: " + str(arcpy.env.workspace) + "\\" + str(FC))

            # output location
            newDistricts_outFC = os.path.join(new_outFolder, "LION_" + FC)
            print ("Districts out = " + str(newDistricts_outFC))
            arcpy.CopyFeatures_management(FC, newDistricts_outFC)
            if FC in bb_cd:
                meta_export(newDistricts_outFC, m_bytes_bb_cd_path, district_name_dict[FC])
            if FC in census:
                meta_export(newDistricts_outFC, m_bytes_census_path, district_name_dict[FC])
                meta_export(newDistricts_outFC, m_census_path, district_name_dict[FC].replace('{} - '.format(FC.upper()), ''))
            if FC in other:
                meta_export(newDistricts_outFC, m_bytes_other_path, district_name_dict[FC])
            if FC in pol:
                meta_export(newDistricts_outFC, m_bytes_pol_admin_path, district_name_dict[FC])
            if FC in fire:
                meta_export(newDistricts_outFC, m_bytes_school_fire_health_path, district_name_dict[FC])
            if FC in bound_munic:
                meta_export(newDistricts_outFC, m_bound_munic_path, district_name_dict[FC].replace('{} - '.format(FC.upper()), ''))
            if FC in bound_school:
                meta_export(newDistricts_outFC, m_bound_school_path, district_name_dict[FC].replace('{} - '.format(FC.upper()), ''))
            if FC in bound_borough:
                meta_export(newDistricts_outFC, m_bound_borough_path, district_name_dict[FC].replace('{} - '.format(FC.upper()), '').replace('.lyr', " (LION).lyr"))
            if FC in bound_pol:
                meta_export(newDistricts_outFC, m_bound_pol_path, district_name_dict[FC].replace('{} - '.format(FC.upper()), ''))
            log.write("" + newDistricts_outFC + "\n")
            print ("---------")
    else:
        print("Districts toggle set to False. If you meant to run Districts, change toggle_districts variable in LION_Districts.ini")

    print("complete, complete")

    # Log file
    EndTime = datetime.datetime.now().replace(microsecond = 0)
    log.write(str(EndTime) + "\t" + str(EndTime - StartTime) + "\n")
    log.close()
    
    arcpy.AcceptConnections(sde, True)


except:
    arcpy.AcceptConnections(sde, True)
    print ("error")
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
        
    pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"
    
    print (pymsg)
    print (msgs)
        
    log.write("" + pymsg + "\n")
    log.write("" + msgs + "")
    log.write("\n")
    log.close()    