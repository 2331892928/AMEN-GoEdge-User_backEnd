import base64
import datetime
import json
import time

from OpenSSL import crypto
from cryptography import x509
import cryptography
from cryptography.hazmat.backends import default_backend

from fastapi import APIRouter, Depends, Cookie, Body
import API.ServerService as ServerService
import API.UserService as UserService
import API.SSLCertService as SSLCertService
import Utils

app = APIRouter(prefix="/SSLCertService", tags=['SSL服务'])


#  将userid放进cookie httponly中

@app.post("/createSSLCert")
async def createSSLCert(UserToken: str = Cookie(None),
                        name: str = Body(None),
                        isCA: bool = Body(None),
                        certData: str = Body(None),
                        keyData: str = Body(None),
                        commons: dict = Depends(Utils.init)):
    #  此时全部是用户token
    config = commons[0]
    ESql = commons[2]
    if ESql is None:
        return Utils.message(393)
    if name is None:
        return Utils.message(201)
    if isCA is None:
        return Utils.message(201)
    if certData is None:
        return Utils.message(201)
    # if keyData is None:
    #     return Utils.message(201)
    api = config['API']
    GoEdge_Api = SSLCertService.SSLCertService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)

    c = base64.b64decode(certData)
    try:
        cert1 = crypto.load_certificate(crypto.FILETYPE_PEM, c)
        # cert.get_issuer().CN  颁发机构
        # cert.get_subject().CN  获得通用名称
        # cert.get_serial_number() 证书SN
        # cert.subject_name_hash()证书hash
        # cert.get_notBefore() 证书生效 b'20221006000000Z'
        # cert.get_notBefore() 证书失效 b'20230104235959Z'
        # print(cert.get_subject())
        cert2 = x509.load_pem_x509_certificate(c, default_backend())
        ski = cert2.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        DNSNameS = ski.value.get_values_for_type(cryptography.x509.DNSName)
        issuer_type = cert1.get_issuer().CN
        issuer_author = cert1.get_issuer().O
        Atime = int(datetime.datetime.strptime(cert1.get_notBefore().decode()[0:-1], '%Y%m%d%H%M%S').timestamp())
        Etime = int(datetime.datetime.strptime(cert1.get_notAfter().decode()[0:-1], '%Y%m%d%H%M%S').timestamp())
    except:
        return Utils.message(389, message="证书不正确")
    SSLinfo = GoEdge_Api.createSSLCert(name=name, isCA=isCA, certData=certData, keyData=keyData, timeBeginAt=Atime,
                                       timeEndAt=Etime, dnsNames=DNSNameS, issuer_type=issuer_type,
                                       issuer_author=issuer_author)
    if not SSLinfo[0]:
        if SSLinfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=SSLinfo[1])
    return Utils.message(200)


@app.post("/listSSLCerts")
async def listSSLCerts(UserToken: str = Cookie(None),
                       UserId: int = Cookie(None),
                       offset: int = Body(),
                       size: int = Body(),
                       keyword: str = Body(None),
                       commons: dict = Depends(Utils.init)):
    config = commons[0]
    api = config['API']
    GoEdge_Api = SSLCertService.SSLCertService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    listSSL = GoEdge_Api.listSSLCerts(UserId, offset, size, keyword)
    countSSL = GoEdge_Api.countSSLCerts(UserId, keyword)
    if not countSSL[0]:
        if countSSL[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=countSSL[1])
    if not listSSL[0]:
        if listSSL[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=listSSL[1])
    try:
        listSSL_V2 = json.loads(base64.b64decode(listSSL[1]).decode())
        for i,v in enumerate(listSSL_V2):
            countInfo = GoEdge_Api.countAllEnabledServersWithSSLCertId(int(v['id']))
            if not countInfo[0]:
                if countInfo[1] is None:
                    return Utils.message(402)
                else:
                    return Utils.message(389, message=countInfo[1])
            listSSL_V2[i]['count'] = countInfo[1]
        listSSL_V2 = base64.b64encode(json.dumps(listSSL_V2).encode('utf-8')).decode("utf-8")
    except:
        return Utils.message(402)
    ret = {
        "count": countSSL[1],
        "data": listSSL_V2
    }
    return Utils.message(200, data=ret)


@app.post("/deleteSSLCert")
async def deleteSSLCert(UserToken: str = Cookie(None),
                        sslCertId: int = Body(None),
                        isOn: bool = Body(None),
                        commons: dict = Depends(Utils.init)):
    config = commons[0]
    api = config['API']
    if sslCertId is None:
        return Utils.message(201)
    GoEdge_Api = SSLCertService.SSLCertService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    sslInfo = GoEdge_Api.deleteSSLCert(sslCertId)
    if not sslInfo[0]:
        if sslInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=sslInfo[1])
    return Utils.message(200)
