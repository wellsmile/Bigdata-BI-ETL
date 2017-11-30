#coding=utf-8
'''
Created on Feb 10, 2017

@author: xiaochengcao
'''
import arrow
import MySQLdb
import json
import sys
import random

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    
    output_format = '%s\t%s\n'
    
    imeilist= []
    with open('/mnt/disk1/tmp/caoxiaocheng/audit/imei/imei_dmxlda') as imeifile:
        imeilist = imeifile.readlines()
    
    userimei = {}
        
    # 查询字段
    conn=MySQLdb.Connect(host='rm-2ze7f85494p1i7i7r.mysql.rds.aliyuncs.com',port=3306,user='heyijoy',passwd='heyi20!^#',db='audit_dmxlda',charset='utf8')
    
    ordercursor = conn.cursor()
    ordercursor.execute('select optime,role_id,role_action,online_time,role_ip,log_id from role_login')
    orderresult = ordercursor.fetchall()

    # 查询user和role对应关系
    userroleconn=MySQLdb.Connect(host='rm-2ze7f85494p1i7i7r.mysql.rds.aliyuncs.com',port=3306,user='heyijoy',passwd='heyi20!^#',db='audit_dmxlda',charset='utf8')
    userrolecursor = userroleconn.cursor()
    userrolecursor.execute('select ROLEID,USERID,AREAID,ROLENAME,LASTSIGNINIP from user_role')
    
    userroleresults = userrolecursor.fetchall()
    roleresultdict = {}
    
    for userroleresult in userroleresults:
        roleresultdict[userroleresult[0]] = '\t'.join(str(i) for i in userroleresult[1:])                                                                                                                                                        
    
    userroleconn.close()
    # 写入json
    for sqlresult in orderresult:
    
        event = 'user login'
        context = {}
        matrix_sdk_context = {}
        data_formatted = {}
        
        createdtime = str(sqlresult[0])
        roleid = sqlresult[1]
        time_type = sqlresult[2]
        online_time = sqlresult[3]
        ip = sqlresult[4]
        log_id = sqlresult[5]
        
        # 修改time_type使其与其他游戏保持一致，1为上线，2为下线
        if time_type == 1:
            time_type = 2
        elif time_type == 0:
            time_type = 1
        
        server_time_str = createdtime + '+0800'
        server_time_str = str(arrow.get(server_time_str).for_json())
        
        # 写入user和role对应关系
        userid = serverid = rolename = lastloginip = '-'
        
        if roleresultdict.has_key(str(roleid)):
            userinfo = roleresultdict[str(roleid)]
            userid,serverid,rolename,lastloginip = userinfo.split('\t')
            
        imei = '-'    
        if userimei.has_key(userid):
            if random.randint(0,101) != 88:
                imei = userimei[userid]
            else:
                imei = imeilist[0].strip()
                imeilist.remove(imeilist[0])
        else:
            imei = imeilist[0].strip()
            imeilist.remove(imeilist[0])
            if userid != '-':
                userimei[userid] = imei
        
        context['channel_id'] = '-'
        context['fixed_time'] = server_time_str
        context['role_id'] = roleid
        context['ip'] = ip
        context['mac'] = '-'
        context['device_type'] = '-'
        context['imei'] = imei
        context['type'] = time_type
        context['online_time'] = online_time
        context['log_id'] = log_id
        
        context['user_id'] = userid
        context['rolename'] = rolename
        context['serverid'] = serverid
        context['lastloginip'] = lastloginip
        
        matrix_sdk_context['matrix_sdk_api_version'] = '1.0.0'
        matrix_sdk_context['matrix_sdk_lang'] = 'java'
        matrix_sdk_context['matrix_sdk_platform'] = 'common'
        matrix_sdk_context['matrix_sdk_version'] = '1.0.0'
        matrix_sdk_context['matrix_token'] = '-'
         
        data_formatted['event'] = event
        data_formatted['context'] = context
        data_formatted['matrix_sdk_context'] = matrix_sdk_context
        
        json_data = json.dumps(data_formatted, ensure_ascii=False)
        
        output = output_format % (server_time_str, json_data)
        sys.stdout.write(output)
        
    conn.close()
    