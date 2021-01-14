import json
import getopt
import sys

def main(argvs):
    # Load config
    config = None
    json_config_file = 'config.json'
    
    try:
        opts, args = getopt.getopt(argvs, '', ['db_username=', 'env_type=', 'db_password=', 
                                                'admin_service_host=', 'manage_service_host=', 'auth_service_host='])
    except getopt.GetoptError as ex:
        print(ex)
        raise ex

    # Open config.json
    try:
        with open(json_config_file , 'r') as config_file:
            config = json.load(config_file)
    
        for opt, arg in opts:

            if opt in ('--db_username', ):
                config['mongodb']['username']= arg
                print('Set database username to %s' % arg)
            elif opt in ('--db_password', ):
                config['mongodb']['password'] = arg
                print('Set database password.')
            elif opt in ('--admin_service_host', ):
                config['test_env']['mission_ctrl']['admin']['host'] = arg
            elif opt in ('--manage_service_host', ):
                config['test_env']['self_service']['manage']['host'] = arg
            elif opt in ('--auth_service_host', ):
                config['test_env']['mission_ctrl']['auth']['host'] = arg
            elif opt in ('--env_type', ):
                config['test_env']['type']=arg

        # Write config.json
        with open(json_config_file, 'w') as outfile:  
            json.dump(config, outfile, indent=4)
        
        print('Done.')

    except Exception as ex:
        print(ex.msg)
        raise ex
    
if __name__=='__main__':
    main(sys.argv[1:])