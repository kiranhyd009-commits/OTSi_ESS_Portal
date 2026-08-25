package com.otsi.ess.data.repository

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.otsi.ess.data.remote.EssApiService
import com.otsi.ess.data.remote.LoginRequest
import com.otsi.ess.data.remote.LoginResponse
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore by preferencesDataStore(name = "auth_prefs")

@Singleton
class AuthRepository @Inject constructor(
    private val apiService: EssApiService,
    @ApplicationContext private val context: Context
) {
    private val ACCESS_TOKEN = stringPreferencesKey("access_token")

    val accessToken: Flow<String?> = context.dataStore.data.map { it[ACCESS_TOKEN] }

    suspend fun login(request: LoginRequest): Result<LoginResponse> {
        return try {
            val response = apiService.login(request)
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                context.dataStore.edit { it[ACCESS_TOKEN] = body.accessToken }
                Result.success(body)
            } else {
                Result.failure(Exception("Login failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun logout() {
        context.dataStore.edit { it.remove(ACCESS_TOKEN) }
    }
}
