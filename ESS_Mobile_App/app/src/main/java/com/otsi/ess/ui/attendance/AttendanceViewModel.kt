package com.otsi.ess.ui.attendance

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.otsi.ess.data.repository.AttendanceRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AttendanceViewModel @Inject constructor(
    private val repository: AttendanceRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<AttendanceUiState>(AttendanceUiState.Idle)
    val uiState: StateFlow<AttendanceUiState> = _uiState

    fun checkIn(lat: Double, lon: Double, isWfh: Boolean) {
        viewModelScope.launch {
            _uiState.value = AttendanceUiState.Loading
            val result = repository.checkIn(lat, lon, isWfh)
            if (result.isSuccess) {
                _uiState.value = AttendanceUiState.Success(result.getOrNull()?.message ?: "Checked in")
            } else {
                _uiState.value = AttendanceUiState.Error(result.exceptionOrNull()?.message ?: "Error")
            }
        }
    }

    fun checkOut() {
        viewModelScope.launch {
            _uiState.value = AttendanceUiState.Loading
            val result = repository.checkOut()
            if (result.isSuccess) {
                _uiState.value = AttendanceUiState.Success(result.getOrNull()?.message ?: "Checked out")
            } else {
                _uiState.value = AttendanceUiState.Error(result.exceptionOrNull()?.message ?: "Error")
            }
        }
    }
}

sealed class AttendanceUiState {
    object Idle : AttendanceUiState()
    object Loading : AttendanceUiState()
    data class Success(val message: String) : AttendanceUiState()
    data class Error(val message: String) : AttendanceUiState()
}
