param(
    [switch]$Setup,
    [switch]$DryRun,
    [switch]$Once,
    [string]$ConfigPath = (Join-Path $PSScriptRoot "wspradar-ab-relay-switch.config.json")
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$script:ToolVersion = "0.1.3"
$script:HidGuid = "4d1e55b2-f16f-11cf-88cb-001111000030"

$nativeCode = @"
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;

public static class WsprAbRelayNative
{
    private const uint GENERIC_READ = 0x80000000;
    private const uint GENERIC_WRITE = 0x40000000;
    private const uint FILE_SHARE_READ = 0x00000001;
    private const uint FILE_SHARE_WRITE = 0x00000002;
    private const uint OPEN_EXISTING = 3;

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    private static extern SafeFileHandle CreateFile(
        string lpFileName,
        uint dwDesiredAccess,
        uint dwShareMode,
        IntPtr lpSecurityAttributes,
        uint dwCreationDisposition,
        uint dwFlagsAndAttributes,
        IntPtr hTemplateFile);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool WriteFile(
        SafeFileHandle hFile,
        byte[] lpBuffer,
        int nNumberOfBytesToWrite,
        out int lpNumberOfBytesWritten,
        IntPtr lpOverlapped);

    [DllImport("hid.dll", SetLastError = true)]
    private static extern bool HidD_GetManufacturerString(
        SafeFileHandle HidDeviceObject,
        byte[] Buffer,
        int BufferLength);

    [DllImport("hid.dll", SetLastError = true)]
    private static extern bool HidD_GetProductString(
        SafeFileHandle HidDeviceObject,
        byte[] Buffer,
        int BufferLength);

    [DllImport("hid.dll", SetLastError = true)]
    private static extern bool HidD_GetSerialNumberString(
        SafeFileHandle HidDeviceObject,
        byte[] Buffer,
        int BufferLength);

    [DllImport("hid.dll", SetLastError = true)]
    private static extern bool HidD_GetFeature(
        SafeFileHandle HidDeviceObject,
        byte[] ReportBuffer,
        int ReportBufferLength);

    [DllImport("hid.dll", SetLastError = true)]
    private static extern bool HidD_SetFeature(
        SafeFileHandle HidDeviceObject,
        byte[] ReportBuffer,
        int ReportBufferLength);

    [DllImport("hid.dll", SetLastError = true)]
    private static extern bool HidD_SetOutputReport(
        SafeFileHandle HidDeviceObject,
        byte[] ReportBuffer,
        int ReportBufferLength);

    public sealed class HidInfo
    {
        public string Manufacturer;
        public string Product;
        public string UsbSerial;
        public byte[] FeatureReport;
    }

    public static HidInfo GetInfo(string path)
    {
        using (SafeFileHandle handle = Open(path, GENERIC_READ | GENERIC_WRITE))
        {
            HidInfo info = new HidInfo();
            info.Manufacturer = GetString(handle, "manufacturer");
            info.Product = GetString(handle, "product");
            info.UsbSerial = GetString(handle, "serial");
            info.FeatureReport = GetFeature(handle);
            return info;
        }
    }

    public static byte[] GetFeatureReport(string path)
    {
        using (SafeFileHandle handle = Open(path, GENERIC_READ | GENERIC_WRITE))
        {
            return GetFeature(handle);
        }
    }

    public static string SetDctRelay(string path, int relayChannel, bool on)
    {
        if (relayChannel < 1 || relayChannel > 9)
        {
            throw new ArgumentOutOfRangeException("relayChannel", "Relay channel must be 1..9.");
        }

        using (SafeFileHandle handle = Open(path, GENERIC_READ | GENERIC_WRITE))
        {
            byte[] report = new byte[9];
            report[0] = 0x00;
            report[1] = on ? (byte)0xFF : (byte)0xFD;
            report[2] = (byte)relayChannel;

            if (HidD_SetFeature(handle, report, report.Length))
            {
                return "HidD_SetFeature";
            }

            int featureError = Marshal.GetLastWin32Error();

            int written;
            if (WriteFile(handle, report, report.Length, out written, IntPtr.Zero) && written > 0)
            {
                return "WriteFile";
            }

            int writeError = Marshal.GetLastWin32Error();
            if (HidD_SetOutputReport(handle, report, report.Length))
            {
                return "HidD_SetOutputReport";
            }

            int outputReportError = Marshal.GetLastWin32Error();
            throw new Win32Exception(outputReportError, "HID relay write failed. HidD_SetFeature error " + featureError + ", WriteFile error " + writeError + ", HidD_SetOutputReport error " + outputReportError + ".");
        }
    }

    private static SafeFileHandle Open(string path, uint access)
    {
        SafeFileHandle handle = CreateFile(
            path,
            access,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            IntPtr.Zero,
            OPEN_EXISTING,
            0,
            IntPtr.Zero);

        if (handle.IsInvalid)
        {
            throw new Win32Exception(Marshal.GetLastWin32Error(), "Could not open HID device: " + path);
        }

        return handle;
    }

    private static string GetString(SafeFileHandle handle, string kind)
    {
        byte[] buffer = new byte[256];
        bool ok;
        if (kind == "manufacturer")
        {
            ok = HidD_GetManufacturerString(handle, buffer, buffer.Length);
        }
        else if (kind == "product")
        {
            ok = HidD_GetProductString(handle, buffer, buffer.Length);
        }
        else
        {
            ok = HidD_GetSerialNumberString(handle, buffer, buffer.Length);
        }

        if (!ok)
        {
            return "";
        }

        return Encoding.Unicode.GetString(buffer).TrimEnd('\0');
    }

    private static byte[] GetFeature(SafeFileHandle handle)
    {
        byte[] buffer = new byte[9];
        buffer[0] = 0x01;
        if (!HidD_GetFeature(handle, buffer, buffer.Length))
        {
            return new byte[0];
        }

        return buffer;
    }
}
"@

if (-not ("WsprAbRelayNative" -as [type])) {
    Add-Type -TypeDefinition $nativeCode
}

function New-DefaultConfig {
    [ordered]@{
        device = [ordered]@{
            vendorId = "16C0"
            productId = "05DF"
            instanceId = $null
            devicePath = $null
            relayChannel = 1
            onMeansTarget = $true
        }
        timing = [ordered]@{
            targetSlotModulo = 0
            referenceSlotModulo = 2
            ntpServer = "time.cloudflare.com"
            ntpCheckMinutes = 15
            warnOffsetMs = 1000
            staleNtpMinutes = 45
            switchLeadMs = 0
        }
        logging = [ordered]@{
            enabled = $true
            path = "wspradar-ab-relay-switch.log"
        }
    }
}

function Save-Config {
    param([object]$Config)
    $Config | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ConfigPath -Encoding UTF8
}

function Read-Config {
    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        $config = New-DefaultConfig
        Save-Config -Config $config
        return $config
    }

    return Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
}

function Convert-InstanceIdToHidPath {
    param([string]$InstanceId)
    $normalized = $InstanceId.ToLowerInvariant().Replace("\", "#")
    return "\\?\$normalized#{$script:HidGuid}"
}

function Convert-FeatureReportToSummary {
    param([byte[]]$Report)

    if (-not $Report -or $Report.Length -eq 0) {
        return [pscustomobject]@{
            Raw = ""
            RelaySerial = ""
            StateMask = $null
        }
    }

    $raw = ($Report | ForEach-Object { $_.ToString("X2") }) -join " "
    $ascii = -join ($Report | Where-Object { $_ -ge 0x20 -and $_ -le 0x7E } | ForEach-Object { [char]$_ })
    $serial = ""
    if ($ascii.Length -ge 5) {
        $serial = $ascii.Substring(0, 5)
    }

    $stateMask = $null
    if ($Report.Length -ge 8) {
        $stateMask = [int]$Report[7]
    }
    if ($Report.Length -ge 9 -and $Report[0] -eq 1) {
        $stateMask = [int]$Report[8]
    }

    return [pscustomobject]@{
        Raw = $raw
        RelaySerial = $serial
        StateMask = $stateMask
    }
}

function Get-RelayDevices {
    param(
        [string]$VendorId = "16C0",
        [string]$ProductId = "05DF"
    )

    $pattern = "HID\VID_$VendorId&PID_$ProductId"
    $entities = @()
    try {
        $entities = Get-CimInstance -ClassName Win32_PnPEntity |
            Where-Object { $_.PNPDeviceID -like "$pattern*" -and $_.PNPClass -eq "HIDClass" }
    }
    catch {
        try {
            $entities = Get-PnpDevice -PresentOnly |
                Where-Object { $_.InstanceId -like "$pattern*" -and $_.Class -eq "HIDClass" } |
                ForEach-Object {
                    [pscustomobject]@{
                        Name = $_.FriendlyName
                        PNPDeviceID = $_.InstanceId
                        Status = $_.Status
                    }
                }
        }
        catch {
            throw "Could not enumerate HID devices through CIM or PnP. $($_.Exception.Message)"
        }
    }

    $devices = @()
    foreach ($entity in $entities) {
        $path = Convert-InstanceIdToHidPath -InstanceId $entity.PNPDeviceID
        $info = $null
        $feature = $null
        $openError = $null
        try {
            $info = [WsprAbRelayNative]::GetInfo($path)
            $feature = Convert-FeatureReportToSummary -Report $info.FeatureReport
        }
        catch {
            $openError = $_.Exception.Message
            $feature = Convert-FeatureReportToSummary -Report @()
        }

        $product = if ($info) { $info.Product } else { "" }
        $relayCount = 1
        if ($product -match "USBRelay(\d+)") {
            $relayCount = [int]$Matches[1]
        }

        $devices += [pscustomobject]@{
            Name = $entity.Name
            InstanceId = $entity.PNPDeviceID
            DevicePath = $path
            Status = $entity.Status
            Manufacturer = if ($info) { $info.Manufacturer } else { "" }
            Product = $product
            UsbSerial = if ($info) { $info.UsbSerial } else { "" }
            RelaySerial = $feature.RelaySerial
            RelayCount = $relayCount
            StateMask = $feature.StateMask
            FeatureRaw = $feature.Raw
            OpenError = $openError
        }
    }

    return $devices
}

function Write-LogLine {
    param(
        [object]$Config,
        [string]$Message
    )

    if (-not $Config.logging.enabled) {
        return
    }

    $logPath = $Config.logging.path
    if (-not [System.IO.Path]::IsPathRooted($logPath)) {
        $logPath = Join-Path $PSScriptRoot $logPath
    }

    $line = "{0:o} {1}" -f [DateTime]::UtcNow, $Message
    Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
}

function Get-WsprSlot {
    param(
        [DateTime]$UtcNow,
        [int]$TargetModulo = 0,
        [int]$ReferenceModulo = 2
    )

    $slotMinute = $UtcNow.Minute
    if (($slotMinute % 2) -ne 0) {
        $slotMinute -= 1
    }

    $slotStart = [DateTime]::new(
        $UtcNow.Year,
        $UtcNow.Month,
        $UtcNow.Day,
        $UtcNow.Hour,
        $slotMinute,
        0,
        [DateTimeKind]::Utc)
    $slotModulo = $slotStart.Minute % 4
    $targetModulo = (($TargetModulo % 4) + 4) % 4
    $referenceModulo = (($ReferenceModulo % 4) + 4) % 4
    $slotName = if ($slotModulo -eq $targetModulo) { "Target" } elseif ($slotModulo -eq $referenceModulo) { "Reference" } else { "Reference" }
    $slotEnd = $slotStart.AddMinutes(2)

    [pscustomobject]@{
        Name = $slotName
        SlotStartUtc = $slotStart
        SlotEndUtc = $slotEnd
        SlotModulo = $slotModulo
    }
}

function Get-DesiredRelayOn {
    param(
        [object]$Config,
        [string]$SlotName
    )

    if ($SlotName -eq "Target") {
        return [bool]$Config.device.onMeansTarget
    }

    return -not [bool]$Config.device.onMeansTarget
}

function Convert-DateTimeToNtpBytes {
    param([DateTime]$UtcTime)

    $epoch = [DateTime]::new(1900, 1, 1, 0, 0, 0, [DateTimeKind]::Utc)
    $span = $UtcTime.ToUniversalTime() - $epoch
    $seconds = [uint32][Math]::Floor($span.TotalSeconds)
    $fraction = [uint32](($span.TotalSeconds - [Math]::Floor($span.TotalSeconds)) * [Math]::Pow(2, 32))

    $bytes = New-Object byte[] 8
    $bytes[0] = ($seconds -shr 24) -band 0xFF
    $bytes[1] = ($seconds -shr 16) -band 0xFF
    $bytes[2] = ($seconds -shr 8) -band 0xFF
    $bytes[3] = $seconds -band 0xFF
    $bytes[4] = ($fraction -shr 24) -band 0xFF
    $bytes[5] = ($fraction -shr 16) -band 0xFF
    $bytes[6] = ($fraction -shr 8) -band 0xFF
    $bytes[7] = $fraction -band 0xFF
    return $bytes
}

function Convert-NtpBytesToDateTime {
    param(
        [byte[]]$Bytes,
        [int]$Offset
    )

    $seconds = ([uint64]$Bytes[$Offset] -shl 24) -bor
        ([uint64]$Bytes[$Offset + 1] -shl 16) -bor
        ([uint64]$Bytes[$Offset + 2] -shl 8) -bor
        [uint64]$Bytes[$Offset + 3]

    $fraction = ([uint64]$Bytes[$Offset + 4] -shl 24) -bor
        ([uint64]$Bytes[$Offset + 5] -shl 16) -bor
        ([uint64]$Bytes[$Offset + 6] -shl 8) -bor
        [uint64]$Bytes[$Offset + 7]

    $milliseconds = ($seconds * 1000.0) + (($fraction * 1000.0) / [Math]::Pow(2, 32))
    $epoch = [DateTime]::new(1900, 1, 1, 0, 0, 0, [DateTimeKind]::Utc)
    return $epoch.AddMilliseconds($milliseconds)
}

function Get-NtpStatus {
    param(
        [string]$Server,
        [int]$TimeoutMs = 3000
    )

    $client = New-Object System.Net.Sockets.UdpClient
    $client.Client.ReceiveTimeout = $TimeoutMs

    try {
        $packet = New-Object byte[] 48
        $packet[0] = 0x1B
        $t1 = [DateTime]::UtcNow
        $t1Bytes = Convert-DateTimeToNtpBytes -UtcTime $t1
        [Array]::Copy($t1Bytes, 0, $packet, 40, 8)

        [void]$client.Connect($Server, 123)
        [void]$client.Send($packet, $packet.Length)
        $remote = New-Object System.Net.IPEndPoint([System.Net.IPAddress]::Any, 0)
        $response = $client.Receive([ref]$remote)
        $t4 = [DateTime]::UtcNow

        if ($response.Length -lt 48) {
            throw "NTP response was too short: $($response.Length) bytes."
        }

        $t2 = Convert-NtpBytesToDateTime -Bytes $response -Offset 32
        $t3 = Convert-NtpBytesToDateTime -Bytes $response -Offset 40
        $offsetMs = (($t2 - $t1).TotalMilliseconds + ($t3 - $t4).TotalMilliseconds) / 2.0
        $delayMs = (($t4 - $t1).TotalMilliseconds - ($t3 - $t2).TotalMilliseconds)

        return [pscustomobject]@{
            Server = $Server
            CheckedUtc = $t4
            OffsetMs = $offsetMs
            DelayMs = $delayMs
            Error = $null
        }
    }
    catch {
        return [pscustomobject]@{
            Server = $Server
            CheckedUtc = [DateTime]::UtcNow
            OffsetMs = $null
            DelayMs = $null
            Error = $_.Exception.Message
        }
    }
    finally {
        $client.Close()
    }
}

function Set-RelayState {
    param(
        [object]$Config,
        [bool]$On
    )

    if ($DryRun) {
        return "DryRun"
    }

    if (-not $Config.device.devicePath) {
        throw "No relay devicePath configured. Run with -Setup first."
    }

    return [WsprAbRelayNative]::SetDctRelay(
        [string]$Config.device.devicePath,
        [int]$Config.device.relayChannel,
        $On)
}

function Format-TimeSpanShort {
    param([TimeSpan]$TimeSpan)
    if ($TimeSpan.TotalSeconds -lt 0) {
        return "0.0 s"
    }

    if ($TimeSpan.TotalMinutes -ge 1) {
        return "{0} min {1:00.0} s" -f [int][Math]::Floor($TimeSpan.TotalMinutes), ($TimeSpan.Seconds + ($TimeSpan.Milliseconds / 1000.0))
    }

    return "{0:0.0} s" -f $TimeSpan.TotalSeconds
}

function Format-SlotMinuteSeries {
    param([int]$Modulo)

    $normalized = (($Modulo % 4) + 4) % 4
    $minutes = 0..59 | Where-Object { ($_ % 4) -eq $normalized } | Select-Object -First 3
    return (($minutes | ForEach-Object { $_.ToString("00") }) -join ", ") + ", ..."
}

function Normalize-WsprSlotModulo {
    param([int]$Modulo)

    $normalized = (($Modulo % 4) + 4) % 4
    if ($normalized -ne 0 -and $normalized -ne 2) {
        throw "Invalid WSPR slot phase '$Modulo'. Use 0 for 00,04,08... or 2 for 02,06,10..."
    }

    return $normalized
}

function Convert-SwitchLeadInputToMs {
    param([string]$InputText)

    $normalized = $InputText.Trim().Replace(",", ".")
    $seconds = 0.0
    if (-not [double]::TryParse(
            $normalized,
            [System.Globalization.NumberStyles]::Float,
            [System.Globalization.CultureInfo]::InvariantCulture,
            [ref]$seconds)) {
        throw "Invalid switch lead '$InputText'. Use seconds, for example 2 or 2.5."
    }

    if ($seconds -lt 0 -or $seconds -gt 8) {
        throw "Invalid switch lead '$InputText'. Use 0 through 8 seconds."
    }

    return [int][Math]::Round($seconds * 1000.0)
}

function Format-SwitchLead {
    param([int]$Milliseconds)

    if ($Milliseconds -le 0) {
        return "0.0 s"
    }

    return "{0:0.0} s" -f ($Milliseconds / 1000.0)
}

function Get-ConfiguredSwitchLeadMs {
    param([object]$Config)

    $property = $Config.timing.PSObject.Properties["switchLeadMs"]
    if ($null -eq $property -or $null -eq $property.Value) {
        return 0
    }

    return [int]$property.Value
}

function Show-Setup {
    $config = Read-Config
    $devices = @(Get-RelayDevices -VendorId $config.device.vendorId -ProductId $config.device.productId)

    Write-Host ""
    Write-Host "WSPRadar A/B Relay Switch setup"
    Write-Host "Tool version: $script:ToolVersion"
    Write-Host ""

    if ($devices.Count -eq 0) {
        Write-Host "No HID relay found for VID:PID $($config.device.vendorId):$($config.device.productId)."
        Write-Host "Check that the relay is plugged in and appears as HID\VID_$($config.device.vendorId)&PID_$($config.device.productId)."
        return
    }

    for ($i = 0; $i -lt $devices.Count; $i++) {
        $d = $devices[$i]
        Write-Host "[$i] $($d.Product) $($d.RelaySerial)"
        Write-Host "    Manufacturer: $($d.Manufacturer)"
        Write-Host "    InstanceId:    $($d.InstanceId)"
        Write-Host "    DevicePath:    $($d.DevicePath)"
        Write-Host "    RelayCount:    $($d.RelayCount)"
        Write-Host "    StateMask:     $($d.StateMask)"
        Write-Host "    FeatureRaw:    $($d.FeatureRaw)"
        if ($d.OpenError) {
            Write-Host "    OpenError:     $($d.OpenError)"
        }
        Write-Host ""
    }

    $selection = 0
    if ($devices.Count -gt 1) {
        $answer = (Read-Host "Select device index").Trim()
        if ($answer -match "^\d+$") {
            $selection = [int]$answer
        }
    }

    if ($selection -lt 0 -or $selection -ge $devices.Count) {
        throw "Invalid device selection: $selection"
    }

    $selected = $devices[$selection]
    $config.device.instanceId = $selected.InstanceId
    $config.device.devicePath = $selected.DevicePath

    $channelAnswer = (Read-Host "Relay channel [default $($config.device.relayChannel)]").Trim()
    if ($channelAnswer -match "^\d+$") {
        $config.device.relayChannel = [int]$channelAnswer
    }

    $mappingAnswer = (Read-Host "Should relay ON mean Target? [Y/n]").Trim()
    if ($mappingAnswer -match "^[Nn]") {
        $config.device.onMeansTarget = $false
    }
    else {
        $config.device.onMeansTarget = $true
    }

    $targetModulo = Normalize-WsprSlotModulo -Modulo ([int]$config.timing.targetSlotModulo)
    $referenceModulo = if ($targetModulo -eq 0) { 2 } else { 0 }
    Write-Host ""
    Write-Host "WSPR A/B slot cadence:"
    Write-Host "    0 = Target at 00,04,08,... and Reference at 02,06,10,..."
    Write-Host "    2 = Target at 02,06,10,... and Reference at 00,04,08,..."
    $targetSlotAnswer = (Read-Host "Target slot phase [0/2, default $targetModulo]").Trim()
    if ($targetSlotAnswer -match "^[02]$") {
        $targetModulo = [int]$targetSlotAnswer
        $referenceModulo = if ($targetModulo -eq 0) { 2 } else { 0 }
    }
    elseif (-not [string]::IsNullOrWhiteSpace($targetSlotAnswer)) {
        throw "Invalid target slot phase '$targetSlotAnswer'. Use 0 or 2."
    }

    $config.timing.targetSlotModulo = $targetModulo
    $config.timing.referenceSlotModulo = $referenceModulo
    Write-Host "Configured Target slots:    $(Format-SlotMinuteSeries -Modulo $targetModulo) UTC minutes"
    Write-Host "Configured Reference slots: $(Format-SlotMinuteSeries -Modulo $referenceModulo) UTC minutes"
    Write-Host ""

    $currentLeadMs = Get-ConfiguredSwitchLeadMs -Config $config
    $leadAnswer = (Read-Host "Switch lead before WSPR slot boundary in seconds [0-8, default $(Format-SwitchLead -Milliseconds $currentLeadMs)]").Trim()
    if (-not [string]::IsNullOrWhiteSpace($leadAnswer)) {
        $currentLeadMs = Convert-SwitchLeadInputToMs -InputText $leadAnswer
    }
    $config.timing.switchLeadMs = $currentLeadMs
    Write-Host "Configured switch lead:     $(Format-SwitchLead -Milliseconds $currentLeadMs) before slot boundary"
    Write-Host ""

    Save-Config -Config $config
    Write-Host ""
    Write-Host "Saved config: $ConfigPath"

    $testAnswer = (Read-Host "Run relay click test now? [y/N]").Trim()
    if ($testAnswer -match "^[Yy]") {
        Write-Host "Turning relay ON for 1 second..."
        [void](Set-RelayState -Config $config -On $true)
        Start-Sleep -Seconds 1
        Write-Host "Turning relay OFF..."
        [void](Set-RelayState -Config $config -On $false)
    }
}

function Show-Dashboard {
    $config = Read-Config
    if (-not $config.device.devicePath) {
        Write-Host "No configured relay. Running setup first."
        Show-Setup
        $config = Read-Config
    }

    $ntp = $null
    $nextNtpCheckUtc = [DateTime]::MinValue
    $lastRelayOn = $null
    $lastSlotName = $null
    $lastRelayError = $null
    $lastWriteMethod = ""

    Write-LogLine -Config $config -Message "START version=$script:ToolVersion dryRun=$DryRun"

    while ($true) {
        $now = [DateTime]::UtcNow
        if ($now -ge $nextNtpCheckUtc) {
            $ntp = Get-NtpStatus -Server $config.timing.ntpServer
            $nextNtpCheckUtc = $now.AddMinutes([int]$config.timing.ntpCheckMinutes)
            if ($ntp.Error) {
                Write-LogLine -Config $config -Message "NTP error server=$($ntp.Server) error=$($ntp.Error)"
            }
            else {
                Write-LogLine -Config $config -Message ("NTP ok server={0} offsetMs={1:0.0} delayMs={2:0.0}" -f $ntp.Server, $ntp.OffsetMs, $ntp.DelayMs)
            }
        }

        $switchLeadMs = Get-ConfiguredSwitchLeadMs -Config $config
        $switchLead = [TimeSpan]::FromMilliseconds($switchLeadMs)
        $currentSlot = Get-WsprSlot -UtcNow $now -TargetModulo ([int]$config.timing.targetSlotModulo) -ReferenceModulo ([int]$config.timing.referenceSlotModulo)
        $relaySlot = Get-WsprSlot -UtcNow $now.AddMilliseconds($switchLeadMs) -TargetModulo ([int]$config.timing.targetSlotModulo) -ReferenceModulo ([int]$config.timing.referenceSlotModulo)
        $desiredRelayOn = Get-DesiredRelayOn -Config $config -SlotName $relaySlot.Name

        if ($null -eq $lastRelayOn -or $desiredRelayOn -ne $lastRelayOn) {
            try {
                $lastWriteMethod = Set-RelayState -Config $config -On $desiredRelayOn
                $lastRelayOn = $desiredRelayOn
                $lastSlotName = $relaySlot.Name
                $lastRelayError = $null
                Write-LogLine -Config $config -Message "RELAY slot=$($relaySlot.Name) relayOn=$desiredRelayOn method=$lastWriteMethod switchLeadMs=$switchLeadMs"
            }
            catch {
                $lastRelayError = $_.Exception.Message
                Write-LogLine -Config $config -Message "RELAY_ERROR slot=$($relaySlot.Name) relayOn=$desiredRelayOn switchLeadMs=$switchLeadMs error=$lastRelayError"
            }
        }

        $relayText = if ($desiredRelayOn) { "ON" } else { "OFF" }
        $mappingText = if ($config.device.onMeansTarget) { "ON=Target, OFF=Reference" } else { "ON=Reference, OFF=Target" }
        $nextSwitchUtc = $relaySlot.SlotEndUtc - $switchLead
        $untilNext = $nextSwitchUtc - $now
        $nextSlotName = if ($relaySlot.Name -eq "Target") { "Reference" } else { "Target" }
        $leadActive = $relaySlot.SlotStartUtc -ne $currentSlot.SlotStartUtc

        $ntpText = "not checked yet"
        $clockState = "Unknown"
        if ($ntp) {
            if ($ntp.Error) {
                $ntpText = "error: $($ntp.Error)"
                $clockState = "NTP failed"
            }
            else {
                $ageMinutes = ($now - $ntp.CheckedUtc).TotalMinutes
                $ntpText = "offset {0:+0.0;-0.0;0.0} ms, delay {1:0.0} ms, checked {2:0.0} min ago via {3}" -f $ntp.OffsetMs, $ntp.DelayMs, $ageMinutes, $ntp.Server
                if ([Math]::Abs([double]$ntp.OffsetMs) -ge [double]$config.timing.warnOffsetMs) {
                    $clockState = "Warning"
                }
                elseif ($ageMinutes -ge [double]$config.timing.staleNtpMinutes) {
                    $clockState = "Stale"
                }
                else {
                    $clockState = "OK"
                }
            }
        }

        Clear-Host
        Write-Host "WSPRadar A/B Relay Switch $script:ToolVersion"
        Write-Host "-----------------------------------"
        Write-Host "Configuration:"
        Write-Host "Mode:              $(if ($DryRun) { 'Dry run' } else { 'Live' })"
        Write-Host "Relay device:      $($config.device.vendorId):$($config.device.productId) CH$($config.device.relayChannel)"
        Write-Host "Relay target:      $relayText ($mappingText)"
        Write-Host "Target slots:      $(Format-SlotMinuteSeries -Modulo ([int]$config.timing.targetSlotModulo)) UTC minutes"
        Write-Host "Reference slots:   $(Format-SlotMinuteSeries -Modulo ([int]$config.timing.referenceSlotModulo)) UTC minutes"
        Write-Host "Switch lead:       $(Format-SwitchLead -Milliseconds $switchLeadMs) before slot boundary"
        Write-Host "Write method:      $lastWriteMethod"
        Write-Host "-----------------------------------"
        Write-Host "UTC:               $($now.ToString('yyyy-MM-dd HH:mm:ss'))"
        Write-Host "NTP:               $ntpText"
        Write-Host "Clock status:      $clockState"
        Write-Host "-----------------------------------"
        Write-Host "Current slot:      $($currentSlot.Name) ($($currentSlot.SlotStartUtc.ToString('HH:mm'))-$($currentSlot.SlotEndUtc.ToString('HH:mm')) UTC, minute $($currentSlot.SlotStartUtc.Minute) mod 4 = $($currentSlot.SlotModulo))"
        if ($leadActive) {
            Write-Host "Relay prepared for: $($relaySlot.Name) ($($relaySlot.SlotStartUtc.ToString('HH:mm'))-$($relaySlot.SlotEndUtc.ToString('HH:mm')) UTC)"
        }
        Write-Host "Next switch to:    $nextSlotName at $($nextSwitchUtc.ToString('HH:mm:ss')) UTC, in $(Format-TimeSpanShort $untilNext)"
        if ($lastRelayError) {
            Write-Host "Relay error:       $lastRelayError"
        }
        Write-Host ""
        Write-Host "Press Ctrl+C to stop."

        if ($Once) {
            break
        }

        Start-Sleep -Milliseconds 500
    }
}

if ($Setup) {
    Show-Setup
}
else {
    Show-Dashboard
}

