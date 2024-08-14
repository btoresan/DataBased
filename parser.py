import json

def parse_data_new(report):
    id = ''
    try:
        id = report['app']['steam']['appId']
    except KeyError as e:
        print('ERROR:', e)
        print(report)
        return None

    time = report['timestamp']

    comment_id = str(id) + str(time)

    significant_bugs = False
    try:
        significant_bugs = report['responses']['significantBugs']
    except KeyError as e:
        print('No significant bugs found at', comment_id)
    
    duration = ''
    try:
        duration = report['responses']['duration']
    except KeyError as e:
        print('No duration found  at', comment_id)

    installs = False
    try:
        installs = report['responses']['installs']
    except KeyError as e:
        print('No installation found at', comment_id)

    opens = False
    try:
        opens = report['responses']['opens']
    except KeyError as e:
        print('No opened found at', comment_id)

    performance_faults = False
    try:
        performance_faults = report['responses']['performanceFaults']
    except KeyError as e:
        print('No performance fault at', comment_id)

    tinker = True
    try:
        tinker = report['responses']['type']
    except KeyError as e:
        print('No tinker at', comment_id)
    
    verdict = False
    try:
        verdict = report['responses']['verdict']
    except KeyError as e:
        print('No verdict at', comment_id)

    system_info = {}
    try:
        system_info = report['systemInfo']
    except KeyError as e:
        print('No system information at', comment_id)

    proton_version = ''
    try:
        proton_version = report['responses']['protonVersion']
    except KeyError as e:
        print('No proton version at', comment_id)

    system_info['protonVersion'] = proton_version

    comment = (comment_id, {
        'appId': id,
        'time': time,
        'significantBugs': significant_bugs,
        'duration': duration,
        'installs': installs,
        'opens': opens,
        'performanceFaults': performance_faults,
        'tinker': tinker,
        'verdict': verdict,
        'systemInfo': system_info
        })

    return comment

def parse_data_old(report):
    id = report['appId']
    time = report['timestamp']

    comment_id = str(id) + str(time)
    
    medal = report['rating']

    significant_bugs = medal != 'Platinum' and medal != 'Gold'
    
    duration = ''

    installs = medal != 'Borked'
    opens = medal != 'Bronze' and installs

    performance_faults = False 

    tinker = medal != 'Platinum'  
    verdict = not tinker or medal == 'Gold'

    system_info = {}
    
    comment = (comment_id, {
        'appId': id,
        'time': time,
        'significantBugs': significant_bugs,
        'duration': duration,
        'installs': installs,
        'opens': opens,
        'performanceFaults': performance_faults,
        'tinker': tinker,
        'verdict': verdict,
        'systemInfo': system_info
        })

    return comment

def parse(aval_list):
    parsed_list = []
    for comment in aval_list:
        parsed_comment = None
        try:
            comment['appId']
            parsed_comment = parse_data_old(comment)
        except KeyError as e:
            parsed_comment = parse_data_new(comment)

        parsed_list.append(parsed_comment)

    print(parsed_list)

with open('report_feb_2024.json', 'r') as report:
    parse(json.load(report))

