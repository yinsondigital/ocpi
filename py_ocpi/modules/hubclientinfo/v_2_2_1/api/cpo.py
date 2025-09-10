
from fastapi import APIRouter, Depends, Request

from py_ocpi.core.schemas import OCPIResponse
from py_ocpi.core.adapter import Adapter
from py_ocpi.core.crud import Crud
from py_ocpi.core.utils import get_auth_token
from py_ocpi.core.dependencies import get_crud, get_adapter
from py_ocpi.core.data_types import CiString
from py_ocpi.core import status
from py_ocpi.core.enums import ModuleID, RoleEnum
from py_ocpi.modules.versions.enums import VersionNumber
from py_ocpi.modules.hubclientinfo.v_2_2_1.schemas import ClientInfo

router = APIRouter(
    prefix='/hubclientinfo',
)


@router.get("/{country_code}/{party_id}", response_model=OCPIResponse)
async def get_hub_client_info(request: Request, country_code: CiString(2), party_id: CiString(3),
                              crud: Crud = Depends(get_crud), adapter: Adapter = Depends(get_adapter)):
    auth_token = get_auth_token(request)

    data = await crud.get(ModuleID.hub_client_info, RoleEnum.cpo, auth_token=auth_token,
                          country_code=country_code, party_id=party_id, version=VersionNumber.v_2_2_1)

    return OCPIResponse(
        data=adapter.hubclientinfo_adapter(data).dict(),
        **status.OCPI_1000_GENERIC_SUCESS_CODE,
    )


@router.put("/{country_code}/{party_id}", response_model=OCPIResponse)
async def update_hub_client_info(request: Request, country_code: CiString(2), party_id: CiString(3),
                                 client_info: ClientInfo,
                                 crud: Crud = Depends(get_crud), adapter: Adapter = Depends(get_adapter)):
    auth_token = get_auth_token(request)

    data = await crud.get(ModuleID.hub_client_info, RoleEnum.cpo, auth_token=auth_token,
                          country_code=country_code, party_id=party_id, version=VersionNumber.v_2_2_1)

    data = await crud.create(ModuleID.hub_client_info, RoleEnum.cpo, client_info.dict(),
                             auth_token=auth_token, country_code=country_code,
                             party_id=party_id, version=VersionNumber.v_2_2_1)


    return OCPIResponse(
        data=[adapter.hubclientinfo_adapter(data).dict()],
        **status.OCPI_1000_GENERIC_SUCESS_CODE,
    )
