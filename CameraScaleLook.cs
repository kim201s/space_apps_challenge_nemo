using System;
using TreeEditor;
using Unity.VisualScripting;
using UnityEngine;

public class CameraScaleLook : MonoBehaviour
{
    [SerializeField] private Transform _originPos;
    [SerializeField] private Transform _sphere;
    
    private Vector3 _earthScale = new Vector3(2, 2, 2);

    private float _initialDistance;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        _initialDistance = Vector3.Distance(transform.position, _originPos.position);
    }

    // Update is called once per frame
    void Update()
    {
        float scrollInput = Input.GetAxis("Mouse ScrollWheel");
        if(Mathf.Abs(scrollInput) > 0){


            //Scaling
            transform.localPosition = new Vector3(transform.localPosition.x, transform.localPosition.y, transform.localPosition.z+scrollInput*3);
            float distance = Vector3.Distance(transform.position ,  _originPos.position);
            float t = Mathf.InverseLerp(_initialDistance/1.2f , _initialDistance/2 , distance );
            float scale = Mathf.Lerp(1, 2, t);
            _sphere.localScale =  _earthScale * scale;

        }
    }
}
