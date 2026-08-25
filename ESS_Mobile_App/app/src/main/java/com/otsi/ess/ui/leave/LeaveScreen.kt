package com.otsi.ess.ui.leave

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun LeaveScreen(
    viewModel: LeaveViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Top
    ) {
        Text("Leave Management", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(32.dp))

        when (val state = uiState) {
            is LeaveUiState.Loading -> CircularProgressIndicator()
            is LeaveUiState.Success -> {
                LeaveBalanceCard("Casual Leave", state.balance.casualLeave)
                Spacer(modifier = Modifier.height(16.dp))
                LeaveBalanceCard("Sick Leave", state.balance.sickLeave)
                Spacer(modifier = Modifier.height(16.dp))
                LeaveBalanceCard("Earned Leave", state.balance.earnedLeave)
            }
            is LeaveUiState.Error -> Text(state.message, color = MaterialTheme.colorScheme.error)
        }
    }
}

@Composable
fun LeaveBalanceCard(label: String, balance: Double) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(label)
            Text(balance.toString(), style = MaterialTheme.typography.bodyLarge)
        }
    }
}
