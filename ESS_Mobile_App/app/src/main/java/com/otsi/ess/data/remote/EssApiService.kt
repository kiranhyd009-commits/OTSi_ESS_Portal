package com.otsi.ess.data.remote

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface EssApiService {
    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("api/attendance/check-in")
    suspend fun checkIn(@Body request: AttendanceRequest): Response<AttendanceResponse>

    @POST("api/attendance/check-out")
    suspend fun checkOut(): Response<AttendanceResponse>

    @GET("api/leave/balance")
    suspend fun getLeaveBalance(): Response<LeaveBalanceResponse>

    @GET("api/profile")
    suspend fun getProfile(): Response<EmployeeProfile>
}
