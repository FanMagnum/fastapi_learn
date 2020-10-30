import random
import pymongo
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder

from app.bgtesks.generate_report import data2file
from app.bgtesks.nvd_spider import spider
from app.core.config import settings
from app.schemas.apps import Data, SpiderResponse

router = APIRouter()

task_ids = (
    '3f8cf077ea2b41cdad03f2d3d6bc8515',
    '9a6562ff5ef549cf8d2ce44e7088a529',
    '7774903487994d069c99585e97e946f6',
    'b8090231ddff40b9866624b0c80d4c6e',
    '159eb341537442779bdc4bb60b839707',
    'b4419d6e6d5744d4a5f02000dc0c13ab',
    '4a24ebdf9bf84fca9e42c5b06cd69bc4',
    '59ebd625934542b597642e631d16b502',
    'ec441d6d0ddd4a059bc0b07ec97fd084',
    '8598cd4236ae414684fa19daa91e4de1',
    '7b913c31e9654dd0b8da0185f33fb59a',
    '380a2cd8d6ea4559a9e34a8ec3ac7dc2',
    '0b688f34918d4588b79e08cfe0982fb9',
    'd14e566bde9246aca7e3ab2a62e2cb0f',
    'f8cce222445947e5adbf0508db694f20',
    'c729b40f0a1f4dd4a9afedab8a53b91d',
    '4efcb02a6ebd4338b97c064f057e5f5a',
    '485e0b712e82485a8af2103c5819d682',
    'b5dc02d45a7647219bf71d673f294aa8',
    '29b2cbc737044dcbab8a06217fdebbff',
    '0c9a0f5267a9446bbc7ea2c843463ceb',
    '6fc5129073e54135a8a5f483e19eb6dc',
    '9f2b926df90d40e9a780e41733763336',
    '56b7c5f522f5477693757acb01dae23e',
    '18902fa7928b4b94b8c7af0b8b83e706',
    'e02c4923ee0f4bcc89b7b0bad48e7a01',
    '4a4b7e0d8fd94d47a70500c9eca78f75',
    '4eac8209ba3e4709b032d88c59723eb3',
    'ff1b02fcbfd040e69023e93abc180f70',
    'dedd73868b844ce08fba82529c6523c1',
    '5e4c5952133640ad86ac32f2b405f953',
    '049c5cbc31d343aa8d8e25622fca7b70',
    '83ea21efaa274b0f8b5945471b3bf773',
    'e05729d6a3e54f658a386be98677e252',
    '500557c42de5426dacde44e7616ccb18',
    'a02e204e4f06478380956dfe093543b9',
    'e1f624a6f49147de9e5a2937ae7244ba',
    '6e234b4c838c45eaa06c05d9af77426c',
    'f11fccc1d69e4dd9935cb36f23cb9b9c',
    'be8b4f77302347c9bc1f444e63171888',
    'c3bec879b9d84f0ebbb7e639e1e9b4c6',
    '25ec48314204425b98e067a17123773e',
    '1f549b9d2b8b4d7d89c339d69b4de4d9',
    'e0a9de6be8464138a89bf6b602670baf',
    '6756057434554e52aba671bda08e9e72',
    '8ed06abe91c1433cbd574a9d0e3d2598',
    '663ae45aab754ec5aecd14cd97f6d5ad',
    '173e5476ff72433bba78f10be3781686',
    '1f7d2834b5e346ae87d1f83fbde9ba55',
    '6b19bb00a1a04ce0acbab740d9fbe46b',
    'bafbd4a74ed04122b0335ae56699a5b1',
    'f24acbc7dd514254b5b548cbc2456c0d',
    '75fc33fb37e64645995307d1c70a0eea',
    '5b0b353c701f426b820c7663228927c5',
    'f2fe6f11db8346cd90ee53969bbfa617',
    '6e5d11f12b4546d99c0495dfa4ae1595',
    '81831046ffc74a68bde8b5aef8013202',
    '1d6a2c38906b4a48962c64b25bb93df4',
    '932122d0949d410299b24c9d129ca20b',
    'ba9f11a0fa8e41048af76eed4f8a4577',
    'd56ac5f588a94efb82f8da1227cb37cc',
    'a8e0aebbd48b44b2be9bb7b9a33e5ba0',
    '753b0b02eb2a45abb396ef050f4674ab',
    '603c6afbb7e349fc896474c5eba3542b',
    '68f58649d2e541a2ac55f04d3085c011',
    '404b471e60224c8d893d58f6d4968075',
    'ce20be80762a4c6783e52666d1eea291',
    '4edbf2dd7e1f4ed4ade9cfcddb7e2104',
    '48af27fcfb324e7298f6b8fbccde70bf',
    'bc007fccc7aa403ebfb82675767291b5',
    '171aa11cd049488e87546a25b656942d',
    '245ed7ecd3de47af83493a1f86e11a3a',
    '655cf1441bc14b7aac88e0b9aedb8a04',
    '1e8d4934414147d28ed464b157a78d09',
    'ef17d20c3b3742d8b8f1d74fa1d8a899',
    '1d8db158172b430f8b6b4dc86512a6f7',
    '7d24f923f20f47e38adcec549fe5ba4e',
    'c0592487fe754c0bac5741e03793ef65',
    '1e260c4fa132443a8dcbcd40d6482712',
    '51dca2f5b84947908fb97c718a1513f9',
    'a9ecbd2b699c40ea9674e61771d88e2a',
    'ae1a1c13a2b744c49e07ca2ae671cc5e',
    '5671779783c14663a885f50d604d66bf',
    '7642b834862b4d99863554a0e83480a9',
    'b110f1513add4278892fb3a4d1571d11',
    'b4d664b07b4c4b9dad4ba97979d51135',
    'a847580735264725b0b77f4c5edf5995',
    '869ea812f31b41d694b712ef3e836c0d',
    '5af26f7d834e4a1f83364df53002dcb6',
    '6024ec769bf4481d9cc12fe511b6795e',
    '04c9d3e55f074561870ba3f6fa4d0bf7',
    'a34e9c1d4bb5428085bcc469b9ace5f3',
    'f85db56bb4484f0b919f4ed86920bfac',
    '0301c064258c4910a5cea68e90f2c4a4',
    '5e4f60342bd24989ad59b9dc264f698f',
    '4660b0ba9d8b41cf94404187c81290ee',
    '8f65b6b991324b6791e6506c7fd3bb57',
    '5e9da3413c3f42c986733dc18d4310c9',
    '98347202a1cd41f9aa457d963c0eda16',
)


@router.post(
    '/',
    response_model=SpiderResponse,
    # response_model_exclude_unset=True,
    # tags=['spider'],
    summary='start spider',
    response_description='Response spider task id'
)
async def start_spider(
        *,
        data: Data,
        background_task: BackgroundTasks
):
    """
    Start spider for apps with below information:
    - **update**: update app info in db, or not
    - **apps**: app info in a list
        - **product**: app name
        - **version**: app version
        - **vendor**: app vendor
    """
    background_task.add_task(spider, jsonable_encoder(data))
    task_id = random.choice(task_ids)
    res = {"message": "success", 'task_id': task_id}
    return res


@router.get("/report")
async def generate_report(task_id: str, background_task: BackgroundTasks):
    if task_id not in task_ids:
        raise HTTPException(status_code=400, detail="Invalid task id")
    background_task.add_task(data2file)
    res = {"message": "generate report success", "url": ""}
    return res
