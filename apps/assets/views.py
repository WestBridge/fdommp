from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.views.generic import View
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
# from rest_framework import status
from .modelform import GaiLanA,GaiLanB

# Create your views here.
import json
from assets import models
from .dao import AssetManage,AutoNewAsset,AutoUpdateAsset,AnsibleAssetsSetup



class AssetView(LoginRequiredMixin,View,AssetManage):
    '''获取资产列表'''
    @method_decorator(permission_required('assets.assets_read','/403/'))
    def get(self,request,*args,**kwargs):
        assets = self.select_all_asset()
        return render(request,'assets/assets_list.html',locals())


class AssetDetailView(LoginRequiredMixin,View,AssetManage):
    '''获取一个资产类型详细数据与更新数据；'''
    def get(self,request,*args,**kwargs):


        asset = self.select_obj_asset(self.query_parm(request)['assetid'])
        meun = self.meun()

        return render(request, 'assets/asset_detail.html', locals())

class AssetManualAdd(LoginRequiredMixin,View,AssetManage):
    def get(self,request, *args, **kwagrs):
        return render(request,'assets/asset_add.html',{'meun':self.meun()})


class AnsibleAssetCreateOrUpdate(LoginRequiredMixin,View,AssetManage,AnsibleAssetsSetup):
    '''手动触发同步所有ansible下的资产'''
    def post(self,request, *args, **kwagrs):
        query_dict = self.query_parm(request)

        if hasattr(self, query_dict['action']):
            func = getattr(self, query_dict['action'])
            return func(request)
        else:
            return HttpResponse(status=404)


    def sync_asset_all(self,request):
        # print (request)
        self.ansible_assets_collect(request)


        return HttpResponse(200)


class AutoAssetCreateOrUpdate(LoginRequiredMixin,View):
    '''处理cmdb客户端发送的数据，新增或更新资产'''
    def post(self,request,*args,**kwargs):
        asset_data = request.POST.get('asset_data')
        data = json.loads(asset_data)
        if not data:
            return HttpResponse('没有数据！')
        if not issubclass(dict, type(data)):
            return HttpResponse('数据必须为字典格式！')
        # 你的检测代码

        sn = data.get('sn', None)

        if sn:
            asset_obj = models.Asset.objects.filter(sn=sn)  # [obj]
            if asset_obj:  # 资产更新
                update_asset = AutoUpdateAsset(request, asset_obj[0], data)
                print('r:', request, 'asset:', asset_obj[0], 'data:', data)
                return HttpResponse('资产数据已经更新。')
            else:  # 资产新增
                obj = AutoNewAsset(request, data)
                response = obj.add_to_new_assets_zone()
                return HttpResponse(response)
        else:
            return HttpResponse('没有资产sn，请检查数据内容！')



