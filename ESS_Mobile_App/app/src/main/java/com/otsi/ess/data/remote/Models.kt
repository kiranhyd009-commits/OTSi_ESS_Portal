package com.otsi.ess.data.remote

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val identifier: String,
    val password: String,
    val role: String
)

data class LoginResponse(
    val message: String,
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    val employee: EmployeeProfile
)

data class EmployeeProfile(
    @SerializedName("employee_id") val employeeId: String,
    val email: String,
    @SerializedName("full_name") val fullName: String,
    val role: String,
    val designation: String?,
    val department: String?,
    @SerializedName("manager_name") val managerName: String?
)

data class AttendanceRequest(
    val latitude: Double,
    val longitude: Double,
    @SerializedName("is_wfh") val isWfh: Boolean
)

data class AttendanceResponse(
    val message: String,
    @SerializedName("check_in_time") val checkInTime: String?,
    @SerializedName("check_out_time") val checkOutTime: String?,
    val status: String
)

data class LeaveBalanceResponse(
    @SerializedName("casual_leave") val casualLeave: Double,
    @SerializedName("sick_leave") val sickLeave: Double,
    @SerializedName("earned_leave") val earnedLeave: Double
)
