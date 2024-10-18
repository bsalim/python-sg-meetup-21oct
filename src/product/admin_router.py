import boto3
import nh3
import random
import string
from decimal import Decimal
from datetime import datetime
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from fastapi import APIRouter, UploadFile, HTTPException, Depends, Form, File, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.product.models import Product, ProductImage, Category
from src.utils import set_flash_message, get_flash_message
from src.auth.utils import login_required, get_current_user
from src.user.models import User

from pydantic import BaseModel
from typing import Optional


router = APIRouter()

templates = Jinja2Templates(directory="templates")

class ParamsValidator(BaseModel):
    session_id: Optional[str]
    product_id: Optional[str]


def validate_params(session_id: Optional[str] = Form(None), product_id: Optional[str] = Form(None)):
    if not session_id and not product_id:
        raise HTTPException(status_code=400, detail="Either session_id or product_id must be provided")
    return ParamsValidator(session_id=session_id, product_id=product_id)


def convert_filename(filename: str) -> str:
    # Convert to lowercase
    filename = filename.lower()
    
    # Replace spaces or dashes with a dash
    filename = filename.replace(" ", "-").replace("--", "-")
    
    # Generate a random hash of 7 lowercase characters
    random_hash = ''.join(random.choices(string.ascii_lowercase, k=7))
    
    # Split the filename into name and extension
    name, ext = filename.rsplit('.', 1)
    
    # Add the hash to the name
    new_filename = f"{name}-{random_hash}.{ext}"
    
    return new_filename


@router.get("/admin/products", response_class=HTMLResponse)
async def get_products(request: Request, response: Response, db: AsyncSession = Depends(get_db),
                       user: User = Depends(get_current_user)):
    result = await db.execute(select(Product).options(
        joinedload(Product.category)).options(
        joinedload(Product.images)).where(Product.user_id == user.id, Product.session_id.is_(None)).order_by(desc(Product.created_at)))
    products_query = result.scalars().unique().all()
    products = []
    
    current_date = datetime.now()
    
    for product in products_query:
        products.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'category': product.category.name,
            'image_url': product.images[0].image_url if product.images else None,
            'price_standard': str(product.price_standard),
            'price_extended': str(product.price_extended),
            'template_filename': str(product.template_filename),
            'created_at': product.created_at.strftime(
                '%b %d' if product.created_at.year == current_date.year else '%b %d, %Y'),
        })
    flash = get_flash_message(request)
    return templates.TemplateResponse(
        request=request, name="product/admin/list.html", context={'title': 'Product list', 
                                                                  'products': products, 'message': flash,
                                                                  'user': request.state.user}
    )


@router.get("/admin/product/new", response_class=HTMLResponse)
async def admin_get_product_new(request: Request, response: Response,
                                db: AsyncSession = Depends(get_db),
                                user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        request=request, name="product/admin/new.html", context={'title': 'Create new product', 'user': request.state.user}
    )


@router.get("/admin/product/edit/{product_id}", response_class=HTMLResponse)
async def admin_get_product_edit(request: Request, response: Response,
                                 product_id: int,
                                 db: AsyncSession = Depends(get_db),
                                 user: User = Depends(get_current_user)):
    result = await db.execute(select(Product).where(
        Product.user_id == user.id, Product.id == product_id))
    product = result.scalars().first()
    return templates.TemplateResponse(
        request=request, name="product/admin/edit.html", 
        context={'title': 'Update your template', 'product': product,
                 'user': request.state.user}
    )


@router.post('/admin/product/new')
async def admin_post_product_new(request: Request,
                                 session_id: str = Form(...),
                                 product_category: str = Form(...),
                                 product_title: str = Form(...),
                                 product_overview: str = Form(...),
                                 product_features: str = Form(...),
                                 product_description: str = Form(...),
                                 product_price_standard: str = Form(...),
                                 product_price_extended: str = Form(...),
                                 product_demo_url: str = Form(None),
                                 db: AsyncSession = Depends(get_db),
                                 user: User = Depends(get_current_user)):
    result = await db.execute(select(Product).where(Product.session_id == session_id))
    product = result.scalars().first()
    
    if not product:
        raise HTTPException('Error occurred.')
    try:
        async with db.begin_nested():
            product.category_id = int(product_category)
            product.name = product_title
            product.description = product_description
            product.overview = product_overview
            product.features = product_features
            product.price_standard = Decimal(product_price_standard)
            product.price_extended = Decimal(product_price_extended)
            product.demo_url = product_demo_url
            product.session_id = None
            
            # result_gallery = await db.execute(select(ProductImage).where(ProductImage.session_id == session_id))
            # product_images = result_gallery.scalars().all()
            await db.execute(
                ProductImage.__table__.update()
                .where(ProductImage.session_id == session_id)
                .values(session_id=None, product_id=product.id)
            )

            # Commit the transaction
            await db.commit()
        return {
            'status': 'ok'
        }
    except Exception as err:
        print(err)
        return {
            'status': 'error'
        }


@router.post('/admin/product/edit')
async def admin_post_product_edit(request: Request,
                                 product_id: int = Form(...),
                                 product_category: str = Form(...),
                                 product_title: str = Form(...),
                                 product_overview: str = Form(...),
                                 product_features: str = Form(...),
                                 product_description: str = Form(...),
                                 product_price_standard: str = Form(...),
                                 product_price_extended: str = Form(...),
                                 product_demo_url: str = Form(...),
                                 db: AsyncSession = Depends(get_db),
                                 user: User = Depends(get_current_user)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    
    if not product:
        raise HTTPException('Error occurred.')
    try:
        async with db.begin_nested():
            product.category_id = int(product_category)
            product.name = product_title
            product.overview = product_overview
            product.description = product_description
            
            product.features = product_features
            product.price_standard = Decimal(product_price_standard)
            product.price_extended = Decimal(product_price_extended)
            product.demo_url = product_demo_url
            product.session_id = None
            
            # Commit the transaction
            await db.commit()
        return {
            'status': 'ok'
        }
    except Exception as err:
        return {
            'status': 'error'
        }
    

@router.get('/admin/product/gallery')
async def admin_get_product_gallery(request: Request, 
                                    session_id: str, 
                                    db: AsyncSession = Depends(get_db),
                                    user: User = Depends(get_current_user)):
    result_gallery = await db.execute(select(ProductImage).where(ProductImage.session_id == session_id))
    product_images = result_gallery.scalars().all()
    
    gallery = []
    for image in product_images:
        gallery.append({
            'id': image.id,
            'image_url': image.image_url
        })
    return gallery


@router.get('/admin/product/{product_id}/gallery')
async def admin_get_product_gallery_by_product_id(request: Request, 
                                    product_id: int, 
                                    db: AsyncSession = Depends(get_db),
                                    user: User = Depends(get_current_user)):
    result_gallery = await db.execute(select(ProductImage).where(ProductImage.product_id == product_id))
    product_images = result_gallery.scalars().all()
    
    gallery = []
    for image in product_images:
        gallery.append({
            'id': image.id,
            'image_url': image.image_url
        })
    return gallery


# @router.post('/admin/product/template/upload')
# async def admin_post_product_template_upload_edit(request: Request,
#                                                   product_id: str = Form(...),
#                                                   template_file: UploadFile = File(...),
#                                                   db: AsyncSession = Depends(get_db),
#                                                   user: User = Depends(get_current_user)):
#     result = await db.execute(select(Product).filter(Product.id == product_id))
#     product = result.scalars().first()
#     if not product:
#         raise HTTPException(status_code=403, detail="Resource existed")
#     s3_client = boto3.client('s3',
#                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                              region_name=settings.AWS_REGION)
#     new_filename = convert_filename(template_file.filename)

#     file_size = round(template_file.size / (1024 * 1024), 2)

#     try:
#         # Initiate the multipart upload
#         multipart_upload = s3_client.create_multipart_upload(
#             Bucket=settings.AWS_S3_BUCKET_NAME, Key=new_filename)
# 
#         parts = []
#         part_number = 1
#         chunk_size = 5 * 1024 * 1024  # 5MB

#         while True:
#             chunk = await template_file.read(chunk_size)
#             if not chunk:
#                 break

#             # Upload the chunk
#             response = s3_client.upload_part(
#                 Bucket=settings.AWS_S3_BUCKET_NAME,
#                 Key=new_filename,
#                 PartNumber=part_number,
#                 UploadId=multipart_upload['UploadId'],
#                 Body=chunk
#             )
#             parts.append({'PartNumber': part_number, 'ETag': response['ETag']})
#             part_number += 1

#         # Complete the multipart upload
#         s3_client.complete_multipart_upload(
#             Bucket=settings.AWS_S3_BUCKET_NAME,
#             Key=new_filename,
#             UploadId=multipart_upload['UploadId'],
#             MultipartUpload={'Parts': parts}
#         )

#         # Update the existing product
#         product.user_id = user.id
#         product.template_filename = new_filename
#         # Save in bytes
#         product.template_filesize = template_file.size
#         await db.commit()
#         return {
#             'status': 'ok',
#             'template_filename': template_file.filename,
#             'template_filesize': file_size
#         }
#     except NoCredentialsError:
#         raise HTTPException(status_code=500, detail="AWS credentials not available")
#     except PartialCredentialsError:
#         raise HTTPException(status_code=500, detail="Incomplete AWS credentials")
#     except Exception as e:
#         # Abort multipart upload in case of error
#         s3_client.abort_multipart_upload(
#             Bucket=settings.AWS_S3_BUCKET_NAME,
#             Key=new_filename,
#             UploadId=multipart_upload['UploadId']
#         )
#         raise HTTPException(status_code=500, detail=str(e))


@router.post('/admin/product/template/upload')
async def admin_post_product_template_new(request: Request,
                                          params: ParamsValidator = Depends(validate_params),
                                          #session_id: str = Form(...),
                                          template_file: UploadFile = File(...),
                                          db: AsyncSession = Depends(get_db),
                                          user: User = Depends(get_current_user)):
    session_id = params.session_id
    product_id = params.product_id
    
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_REGION)
    new_filename = convert_filename(template_file.filename)

    file_size = round(template_file.size / (1024 * 1024), 2)

    try:
        # Initiate the multipart upload
        multipart_upload = s3_client.create_multipart_upload(
            Bucket=settings.AWS_S3_BUCKET_NAME, Key=new_filename)

        parts = []
        part_number = 1
        chunk_size = 5 * 1024 * 1024  # 5MB

        while True:
            chunk = await template_file.read(chunk_size)
            if not chunk:
                break

            # Upload the chunk
            response = s3_client.upload_part(
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=new_filename,
                PartNumber=part_number,
                UploadId=multipart_upload['UploadId'],
                Body=chunk
            )
            parts.append({'PartNumber': part_number, 'ETag': response['ETag']})
            part_number += 1

        # Complete the multipart upload
        s3_client.complete_multipart_upload(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=new_filename,
            UploadId=multipart_upload['UploadId'],
            MultipartUpload={'Parts': parts}
        )
        if session_id:
            result = await db.execute(select(Product).filter(Product.session_id == session_id))
        else:
            result = await db.execute(select(Product).filter(Product.id == product_id))
        product = result.scalars().first()

        if product:
            # Update the existing product
            product.user_id = user.id
            product.template_filename = new_filename
            # Save in bytes
            product.template_filesize = template_file.size
        else:
            # Create a new product
            new_product = Product(session_id=session_id, user_id=user.id, template_filename=new_filename, template_filesize=template_file.size)
            db.add(new_product)
        await db.commit()
        status = 'success'
        message = 'Your template has been successfully created.'
        set_flash_message(request, message, status)
        return {
            'status': 'ok',
            'template_filename': template_file.filename,
            'template_filesize': file_size
        }
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available")
    except PartialCredentialsError:
        raise HTTPException(status_code=500, detail="Incomplete AWS credentials")
    except Exception as e:
        # Abort multipart upload in case of error
        s3_client.abort_multipart_upload(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=new_filename,
            UploadId=multipart_upload['UploadId']
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/admin/product/gallery/upload')
async def admin_post_upload_gallery(request: Request,
                                    filepond: UploadFile,
                                    params: ParamsValidator = Depends(validate_params),
                                    db: AsyncSession = Depends(get_db),
                                    user: User = Depends(get_current_user)):
    session_id = params.session_id
    product_id = params.product_id
    
    s3_client = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_REGION)
    
    folder_name = 'gallery'  # Specify the folder name or prefix
    image_filename = convert_filename(filepond.filename)
    # Construct the key with the folder prefix and file name
    key = f"{folder_name}/{image_filename}"

    try:
        # Upload file to S3 with the specified key (folder/prefix + filename)
        resp = s3_client.upload_fileobj(filepond.file, settings.AWS_S3_BUCKET_NAME,
                                        key, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
        image_url= f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        # Save along with session
        if session_id:
            kwargs = {
                'session_id': session_id
            }
        else:
            kwargs = {
                'product_id': int(product_id)
            }
        product_image = ProductImage(user_id=user.id,
                                     image_url=image_url,
                                     image_name=image_filename,
                                     image_size=filepond.size,
                                     **kwargs)
        db.add(product_image)
        await db.commit()
        return {
            'status': 'ok',
            'message': 'Gallery uploaded successfully.',
        }
    except Exception as err:
        print(err)
        return {
            'status': 'error',
            'message': 'Error occurred. Please try again later',
        }


@router.get('/admin/product/template')
async def admin_get_product_template(request: Request, session_id: str, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(Product).where(Product.session_id == session_id))
        product = result.scalars().first()
    
    # Check if template_filename is not None
    if product and product.template_filename:
        return {
            'exists': True,
            'template_filename': product.template_filename,
            'template_filesize': round(product.template_filesize / (1024 * 1024), 2) if product.template_filesize else 0
        }
    return {
        'exists': False
    }


@router.get('/admin/product/{product_id}/template')
async def admin_get_product_template_by_product(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
    
    # Check if template_filename is not None
    if product and product.template_filename:
        return {
            'exists': True,
            'template_filename': product.template_filename,
            'template_filesize': round(product.template_filesize / (1024 * 1024), 2) if product.template_filesize else 0
        }
    return {
        'exists': False
    }


@router.delete('/admin/product/template')
async def admin_delete_product_template(session_id: str,
                                        db: AsyncSession = Depends(get_db),
                                        user: User = Depends(get_current_user)):
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_REGION)

    result = await db.execute(select(Product).where(Product.session_id == session_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    template_filename = product.template_filename

    if template_filename:
        # Delete the file from S3
        try:
            s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=template_filename)
            product.template_filename = None
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="AWS credentials not found")
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file from S3: {e}")
    await db.commit()
    
    return {
        'status': 'ok',
        'message': 'Your template file has been removed'
    }



@router.delete('/admin/product/template-by-product')
async def admin_delete_product_template_by_product_id(product_id: int,
                                                      db: AsyncSession = Depends(get_db),
                                                      user: User = Depends(get_current_user)):
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_REGION)

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    template_filename = product.template_filename

    if template_filename:
        # Delete the file from S3
        try:
            s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=template_filename)
            product.template_filename = None
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="AWS credentials not found")
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file from S3: {e}")
    await db.commit()
    
    return {
        'status': 'ok',
        'message': 'Your template file has been removed'
    }


@router.delete('/admin/product/image/{image_id}')
async def admin_delete_image_by_id(image_id: int,
                                   db: AsyncSession = Depends(get_db),
                                   user: User = Depends(get_current_user)):
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_REGION)

    result = await db.execute(select(ProductImage).where(ProductImage.id == image_id, ProductImage.user_id == user.id))
    image = result.scalars().first()
    if not image:
        raise HTTPException(status_code=401, detail="Product not found")
    try:
        s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET_NAME, 
                                Key=f'{settings.S3_IMAGE_FOLDER}/{image.image_name}')
        await db.delete(image)
        await db.commit()
        return {
            'status': 'ok',
            'message': 'Image has been removed'
        }

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="AWS credentials not found")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file from S3: {e}")
