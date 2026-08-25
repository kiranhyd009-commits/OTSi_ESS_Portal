package com.otsi.ess

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.otsi.ess.data.repository.AuthRepository
import com.otsi.ess.ui.attendance.AttendanceScreen
import com.otsi.ess.ui.leave.LeaveScreen
import com.otsi.ess.ui.auth.LoginScreen
import com.otsi.ess.ui.dashboard.DashboardScreen
import com.otsi.ess.ui.theme.OtsiESSPortalTheme
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var authRepository: AuthRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            OtsiESSPortalTheme {
                val navController = rememberNavController()
                val token by authRepository.accessToken.collectAsState(initial = null)
                
                val startDestination = if (token != null) "dashboard" else "login"

                NavHost(navController = navController, startDestination = startDestination) {
                    composable("login") {
                        LoginScreen(onLoginSuccess = {
                            navController.navigate("dashboard") {
                                popUpTo("login") { inclusive = true }
                            }
                        })
                    }
                    composable("dashboard") {
                        DashboardScreen(
                            onLogout = {
                                navController.navigate("login") {
                                    popUpTo("dashboard") { inclusive = true }
                                }
                            },
                            onNavigateToAttendance = {
                                navController.navigate("attendance")
                            },
                            onNavigateToLeave = {
                                navController.navigate("leave")
                            }
                        )
                    }
                    composable("attendance") {
                        AttendanceScreen()
                    }
                    composable("leave") {
                        LeaveScreen()
                    }
                }
            }
        }
    }
}
