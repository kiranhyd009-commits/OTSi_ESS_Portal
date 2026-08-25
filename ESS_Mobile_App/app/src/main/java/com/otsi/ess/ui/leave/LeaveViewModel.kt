package com.otsi.ess.ui.leave

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.otsi.ess.data.remote.EssApiService
import com.otsi.ess.data.remote.LeaveBalanceResponse
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LeaveViewModel @Inject constructor(
    private val apiService: EssApiService
) : ViewModel() {

    private val _uiState = MutableStateFlow<LeaveUiState>(LeaveUiState.Loading)
    val uiState: StateFlow<LeaveUiState> = _uiState

    init {
        fetchLeaveBalance()
    }

    fun fetchLeaveBalance() {
        viewModelScope.launch {
            _uiState.value = LeaveUiState.Loading
            try {
                val response = apiService.getLeaveBalance()
                if (response.isSuccessful && response.body() != null) {
                    _uiState.value = LeaveUiState.Success(response.body()!!)
                } else {
                    _uiState.value = LeaveUiState.Error("Failed to fetch balance")
                }
            } catch (e: Exception) {
                _uiState.value = LeaveUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class LeaveUiState {
    object Loading : LeaveUiState()
    data class Success(val balance: LeaveBalanceResponse) : LeaveUiState()
    data class Error(val message: String) : LeaveUiState()
}
