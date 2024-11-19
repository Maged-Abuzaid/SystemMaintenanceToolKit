
# System Maintenance Toolkit

A GUI-based toolkit for performing essential system maintenance tasks on Windows. The toolkit provides a user-friendly interface to execute system health checks, disk cleanup, and defragmentation and optimization of drives.

## Features

- **System Health Check**: Automates the execution of DISM and SFC commands to check and repair system health.
- **Disk Cleanup**: Cleans temporary files and unnecessary directories to free up disk space.
- **Defragment and Optimize Drives**: Defragments and optimizes specified drives to improve system performance.
- **Logging**: Generates detailed logs for each operation, which can be viewed within the application.
- **Clear Logs**: Provides an option to clear all generated logs.

## Requirements

- **Operating System**: Windows 7 or later (Administrator privileges required).

## Installation

1. **Download the Executable**:

   - Obtain the `SystemMaintenanceToolkit.exe` file from the provided source or [Releases](#) page.

2. **Place the Executable**:

   - Copy the `SystemMaintenanceToolkit.exe` file to a directory of your choice.

   **Note**: The application is self-contained and does not require any additional files or installation steps.

## Usage

1. **Run the Application with Administrative Privileges**:

   - Right-click on `SystemMaintenanceToolkit.exe` and select **"Run as administrator"**.

2. **Using the Application**:

   - **System Health Check**:
     - Click on the **"Start"** button under the **"System Health Check"** section to begin the health check process.
     - View logs by clicking the **"See Log"** button.
   - **Disk Cleanup**:
     - Click on the **"Clean"** button under the **"Disk Cleanup"** section to remove temporary files.
     - View logs by clicking the **"See Log"** button.
   - **Defragment and Optimize Drives**:
     - Click on the **"Optimize"** button under the **"Defragment and Optimize Drives"** section to start defragmentation.
     - View logs by clicking the **"See Log"** button.
   - **Clear Logs**:
     - Click the **"Clear Logs"** button at the top to delete all existing log files.

   **Important**: The application requires administrative privileges to perform certain operations. Always run the application as an administrator.

## Logging

- **Log Storage**: Logs are stored in a `logs` directory, which will be created in the same location as the executable.
- **Per-Operation Logs**: Each operation has its own log file for easy troubleshooting.
- **Viewing Logs**: Use the **"See Log"** buttons to view logs within the application.

## Customization

- **Defragment and Optimize Drives**:

  The application is set to defragment drives `C:` and `D:` by default. If you need a customized version to target different drives, please contact the developer.

- **Cleanup Paths**:

  The application targets specific directories for disk cleanup. If you require different cleanup paths, please contact the developer for a customized version.

## Troubleshooting

- **Administrator Privileges**:

  Some operations require administrative privileges. If you encounter errors, make sure to run the application as an administrator.

- **Missing Logs or Issues with UI**:

  If the application is not displaying correctly or logs are not being saved, ensure that the executable has permission to create directories and files in its location.

- **Antivirus Warnings**:

  Some antivirus programs may flag executables that perform system-level operations. If you trust the source of the executable, you may need to whitelist it in your antivirus software.

## Support

If you encounter any issues or have questions about the application, please reach out via email at [MagedM.Abuzaid@gmail.com](mailto:MagedM.Abuzaid@gmail.com).

## Updates

Check the [Releases](#) page periodically for updates or new versions of the application.

## Acknowledgments

- **Contributors**: Thank you to all the contributors who have helped improve this project.
- **Libraries and Tools**: This application was built using Python's standard libraries and Tkinter for the GUI.

## Feedback

Your feedback is valuable to us. Please consider providing feedback or suggestions to help us improve the application.

## Frequently Asked Questions (FAQ)

### Q: Do I need to install Python to run this application?

**A**: No, the executable is a standalone application and does not require Python to be installed on your system.

### Q: Can I customize the drives and paths the application targets?

**A**: The default executable targets specific drives and paths. If you need customization, please contact the developer for a tailored version.

### Q: Is it safe to use this application?

**A**: The application performs system maintenance tasks that are generally safe. However, it is always recommended to back up important data before performing system-level operations.

### Q: How can I verify that the application is safe to run?

**A**: The application is open-source, and the source code is available for review. You can also scan the executable with antivirus software.

## Known Issues

- **Disk Cleanup Paths**: Some files may not be deleted due to permission issues or if they are in use by other programs.
- **Defragmentation Limitations**: Defragmentation may not be effective on SSDs and is generally not recommended for them.

## License and Usage Terms

This software is proprietary and all rights are reserved by the developer.

### **Usage Permissions**

- **Personal Use**: You are permitted to use and modify the software for personal, non-commercial purposes.
- **No Redistribution**: You may not redistribute, share, or sublicense the software or any modified versions of it.
- **No Commercial Use**: Commercial use of this software is prohibited without explicit permission from the developer.

### **Attribution**

- **No Claim of Ownership**: You may not claim ownership or authorship of the original software.
- **No Removal of Notices**: You may not remove or alter any proprietary notices or labels on the software.

### **Disclaimer of Liability**

The software is provided "as is," without warranty of any kind, express or implied. In no event shall the developer be liable for any claim, damages, or other liability arising from the use of the software.

---

**Disclaimer**: This tool performs system-level operations and should be used with caution. Always ensure you have backups of important data before running system maintenance tasks.

---

**Note**: By using this software, you agree to the terms outlined in the **License and Usage Terms** section.

Additional Notes
Custom License: The license section above is a custom proprietary license tailored to your requirements. It restricts copying, redistribution, and holds you harmless from liability.
Legal Considerations: While this license aims to cover your needs, it's advisable to consult with a legal professional to ensure it fully protects your interests and complies with applicable laws.
Important Considerations
Sharing on GitHub: Be aware that hosting code on a public GitHub repository without a license doesn't prevent others from viewing or forking the repository, as per GitHub's Terms of Service. If you wish to keep the code private, consider using a private repository.
Liability: Including a disclaimer of liability is important, but its enforceability can vary by jurisdiction. Legal advice is recommended.
