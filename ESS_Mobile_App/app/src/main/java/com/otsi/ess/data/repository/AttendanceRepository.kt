package com.otsi.ess.data.repository

import com.otsi.ess.data.remote.AttendanceRequest
import com.otsi.ess.data.remote.AttendanceResponse
import com.otsi.ess.data.remote.EssApiService
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AttendanceRepository @Inject constructor(
    private val apiService: EssApiService
) {
    suspend fun checkIn(latitude: Double, longitude: Double, isWfh: Boolean): Result<AttendanceResponse> {
        return try {
            val response = apiService.checkIn(AttendanceRequest(latitude, longitude, isWfh))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Check-in failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun checkOut(): Result<AttendanceResponse> {
        return try {
            val response = apiService.checkOut()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Check-out failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
