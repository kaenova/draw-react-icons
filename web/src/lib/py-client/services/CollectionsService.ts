/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectionInfo } from '../models/CollectionInfo';
import type { Icon } from '../models/Icon';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class CollectionsService {

    /**
     * Get Collections
     * @returns CollectionInfo Successful Response
     * @throws ApiError
     */
    public static getCollectionsCollectionsGet(): CancelablePromise<Array<CollectionInfo>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/collections',
        });
    }

    /**
     * Query Collections
     * @param token 
     * @param collectionName 
     * @param base64Image 
     * @param normalizeImage 
     * @param invertImage 
     * @param limit 
     * @returns Icon Successful Response
     * @throws ApiError
     */
    public static queryCollectionsCollectionsQueryPost(
token: string,
collectionName: string,
base64Image: string,
normalizeImage: boolean = true,
invertImage: boolean = false,
limit: number = 20,
): CancelablePromise<Array<Icon>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/collections/query',
            query: {
                'token': token,
                'collectionName': collectionName,
                'base64Image': base64Image,
                'normalizeImage': normalizeImage,
                'invertImage': invertImage,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
