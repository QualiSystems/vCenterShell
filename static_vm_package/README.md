This article explains how to add a VM, which already exists on a vCenter server, as a CloudShell inventory resource. Once added to CloudShell, users will be able to add the VM resource to their blueprint and sandbox diagrams and use it like a regular resource. The vCenter Static VM shell is provided for this purpose.

This is useful if the VM is too complex or time consuming to power on or off, or if the VM is always on and is not added or deleted from the vCenter as part of the sandbox lifecycle. For example, in VMs that maintain a database or a production server.

* **Note:** CloudShell does not automatically power off static VMs at the end of the sandbox because they are commonly used as shared resources.*

**To load an existing VM as a resource:**

1. Download the vCenter Static VM shell.

<br>If you choose to develop your own shell, make sure it has an Autoload command and supports loading the VM's information into CloudShell.

2. Import the vCenter Static VM shell into CloudShell Portal.

<br>You can drag the shell's zip file into CloudShell Portal or use the **Import Package** option in the user menu.

3. In the **Inventory** dashboard, in the **Resources** tab, click the folder in which you want to create the resource.

4. Click **Add New**.

5. In the **Create New Resource** dialog box, select the **vCenter Static VM** Shell from the list.

6. Enter a *Name** for the VM resource that you want to create in CloudShell.

<br>* **Note:** The resource's name has a limit of 100 characters and can only contain alpha-numeric characters, spaces, and the following characters: | . - _ ] [*

7. In the **Address** field, enter the IP address of the VM, or enter **na** if the IP address is not known or does not exist.

8. Click **Create**.

<br>The **Resource** dialog box is displayed.

9. Enter the required information.

* **vCenter Name**: vCenter cloud provider resource. The cloud provider resource defines the settings of the VM's vCenter server and provides commands such as **Power On**, **Refresh IP** and connectivity commands for the resource in the sandbox. For additional information, see (Adding VMware vCenter Cloud Provider Resource)[https://help.quali.com/Online%20Help/9.2/Portal/Content/CSP/INVN/Add-vCenter-Shell.htm].
vCenter VM: Path to the vCenter VM. The path is relative to the datacenter defined in the selected vCenter cloud provider resource and must include the VM's name. For example: *Temp/My VM*

<br>* **Note:** If the VM is powered off, the end user will need to power it on in the sandbox.*

10. Click **Start Discovery**.

<br>When the discovery process completes, a confirmation message is displayed. The resource is displayed in the **Inventory** dashboard and can be used in blueprints and sandboxes.

<br>In the sandbox, the VM resource behaves like the VM of a deployed App and uses the commands provided by the vCenter cloud provider, as explained in (Run App commands)[https://help.quali.com/Online%20Help/9.2/Portal/Content/CSP/LAB-MNG/Sndbx-Use-Apps.htm#Running].
