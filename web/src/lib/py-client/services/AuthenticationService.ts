/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class AuthenticationService {

    /**
     * Check Token
     * @param token 
     * @returns boolean Successful Response
     * @throws ApiError
     */
    public static checkTokenAuthGet(
token: string,
): CancelablePromise<boolean> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth',
            query: {
                'token': token,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Token
     * @param hCaptchaToken 
     * @returns string Successful Response
     * @throws ApiError
     */
    public static createTokenAuthTokensPost(
hCaptchaToken: string,
): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/tokens',
            query: {
                'hCaptchaToken': hCaptchaToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
