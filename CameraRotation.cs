using System;

using UnityEngine;


public class CameraRotation : MonoBehaviour
{
    [Header("Values")]

    [SerializeField] private float _forceX = 5;
    [SerializeField] private float _forceY = 5;



    private float _applyX;
    private float _applyY;
    private float _additionalForceX = 0;
    private float _additionalForceY = 0;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
   

    // Update is called once per frame
    void Update()
    {
        ApplyRotation();
    }

    private void ApplyRotation()
    {
        if(Input.GetMouseButton(0)){
            float MouseX = Input.GetAxis("Mouse X");
            float MouseY = Input.GetAxis("Mouse Y");

            _additionalForceX = (Mathf.Abs(MouseX) > 0) ? 1 : 0;
            _additionalForceY = (Mathf.Abs(MouseY) > 0) ? 1 : 0;
        
            //apply force
            _applyX = _forceX*MouseX;
            _applyY = _forceY*MouseY;

            transform.Rotate(Vector3.up*_applyX + Vector3.left*_applyY);
        }
        else
        {
            //additionla force
            transform.Rotate(Vector3.up*_additionalForceX + Vector3.right*_additionalForceY);
            _additionalForceX = _additionalForceX > 0 ? _additionalForceX-0.1f : 0;  
            _additionalForceY = _additionalForceY > 0 ? _additionalForceY-0.1f : 0;

        }
    }
}
