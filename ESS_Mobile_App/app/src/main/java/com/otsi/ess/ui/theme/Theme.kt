package com.otsi.ess.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColorScheme = lightColorScheme(
    primary = OtsiNavy,
    secondary = OtsiBlue,
    tertiary = OtsiGreen,
    background = BgGray,
    surface = Color.White
)

@Composable
fun OtsiESSPortalTheme(
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = LightColorScheme,
        typography = Typography,
        content = content
    )
}
