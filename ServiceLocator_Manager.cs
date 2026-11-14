using System;
using Unity.VisualScripting;
using UnityEngine;


[DefaultExecutionOrder(-99)]
public class ServiceLocator_Manager : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    [Header("References")]
    [SerializeField] private EarthData _earthData;
    [SerializeField] private MarkerManager _markerManager;
    [SerializeField] private Marker _markerFactory;
    
    


    private void Awake()
    {
        //Register Services
        ServiceLocator.Current.Register<GetTheEarth>(_earthData);
        ServiceLocator.Current.Register<IMarkerManager>(_markerManager);
        ServiceLocator.Current.Register<IMarker>(_markerFactory);
    }
}
